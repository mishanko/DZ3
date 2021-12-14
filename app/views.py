from flask_restx import Resource
from app import api, models_dao, celery
from app import db_model
import os
from joblib import dump, load
from app import metrics

from log import log
from typing import Tuple, Union, NoReturn

from sklearn.linear_model import LogisticRegression as LR
from sklearn.tree import DecisionTreeClassifier as DT
import numpy as np


# * Словарь моделей, доступных для обучения
models = {1:LR,
          2:DT}

@api.route('/api/ml_models')
class MLModels(Resource):
    """Класс для отображения списка доступных для обучения моделей
       и гиперпараметров
    """
    @metrics.counter('cnt_gets', 'Number_of_gets', labels={'status': lambda resp:resp.status_code})
    def get(self) -> list:
        log.info(f'Trained models = {models_dao._trained_models}')
        return models_dao._ml_models


@api.route('/api/ml_models/<int:id>')
class MLModel(Resource): 
    """Класс для отображения конкретной модели
       и её гиперпараметров
    """

    def get(self, id:int) -> Union[Tuple[dict, dict], NoReturn]:
        try:
            name = models_dao._ml_models[id-1]["name"]
            trained = models_dao._ml_models[id-1]["trained"]
            log.info(f'MODEL id = {id} class = {name} trained = {trained}')
            model = db_model.view_all(id)
            return model, 200
        except IndexError as e:
            log.error("Entered invalid model ID")
            api.abort(404, e)


@api.route('/api/ml_models/<int:id>/train')
class MLModelTrain(Resource): 
    """Класс для обучения
    """
    
    def put(self, id:int) -> Tuple[dict, int]:
        model = self._train(id)
        model = load(model)
        self._save_model(model, id)
        data = {'trained': True} 
        log.info("Model 'trained' status changed to True")
        return models_dao.update(id, data), 200

    def _train(self, id:int) -> Union[DT, LR, NoReturn]:
        log.info("Preparing to train...",)
        try: 
            df = api.payload
            if 'H' in df.keys():
                hypers = df['H']
                log.info(f"Model's hyperparameters: {hypers}")
                model = models[id](**hypers)
            else:
                model = models[id]()
            X = df['X']
            y = df['y']
            log.info("Start training",)
            
            path = f'./worker/models/model_{models_dao.num}.joblib'
            dump(model, path)
            # посылаем в контенер для обучения
            task = celery.send_task("train", args=[X, y, path])
            
            log.info("Training finished!")
            return path
        except KeyError or AttributeError as e:
            log.error("Looks like you either forget X or y values")
            api.abort(404, e)

    def _save_model(self, model:Union[DT, LR], id:int):
        log.info(f"Saving the model...")
        models_dao._trained_models[id][str(models_dao.num)] = model
        path = f'./worker/models/model_{models_dao.num}.joblib'
        self._add_to_bd(path, int(id))
        # log.info(f"Trained models: {models_dao._trained_models}")
        models_dao.num += 1

    def _add_to_bd(self, path, id): 
        item_doc = {
            'id': models_dao.num,
            'num': id,
            'path': path
            }
        db_model.post(item_doc)
        log.info(f"Model saved and added to DB {db_model.get(int(models_dao.num))}")
        # log.info(db_model.get(int(models_dao.num)))


@api.route('/api/ml_models/<int:id>/predict')
class MLModelPredict(Resource): 
    """Класс для предсказания
    """

    def post(self, id:int) -> Tuple[dict, int]: 
        prediction = self._predict()
        log.info(f"Here is the prediction: {prediction} for {id}")
        return prediction, 200


    def _predict(self) -> Union[dict, NoReturn]:
        try:
            df = api.payload
            number = df['num']
            model = db_model.get(int(number))
            model = load(model['path'])
            X_new = np.fromiter(df['X'], dtype=float)
            # log.info(model)
            prediction = {'Prediction': str(model.predict([X_new]))}
            return prediction
        except KeyError as e:
            log.error("Invalid model number or No trained models")
            api.abort(404, e)


@api.route('/api/ml_models/<int:id>/delete')
class MLModelDelete(Resource): 
    """Класс для удаления
    """

    def delete(self, id:int) -> Union[Tuple[str, int], NoReturn]:
        try: 
            df = api.payload
            num = df['num']
            if num in models_dao._trained_models[id].keys():
                models_dao.delete(id, num)
                path = db_model.get(id=int(num))['path']
                # log.info(path)
                db_model.delete(id=int(num))
                os.system(f"rm -rf {path}")
                log.info(f"Model {num} deleted")
                return '', 204
            else:
                log.error("No model with this number")
                api.abort(404, "WARNING: No model with this number")

        except KeyError as e:
            log.error("ERROR: Invalid model number")
            api.abort(404, e)


@api.route('/api/ml_models/<int:id>/retrain')
class MLModelRetrain(MLModelTrain): 
    """Класс для переобучения модели
    """

    def _train(self, id:int) -> Union[DT, LR]:
        log.info("INFO: Prepating to retrain...",)
        try: 
            df = api.payload
            if 'H' in df.keys():
                hypers = df['H']
                model = models[id](**hypers)
            else:
                model = models[id]()
            X = df['X']
            y = df['y']
            self.num = str(df['num'])
            log.info("Start training")
            
            path = f'./worker/models/model_{self.num}.joblib'
            dump(model, path)
            task = celery.send_task("train", args=[X, y, path])
            
            log.info("Training finished!")
            return path
        except KeyError as e:
            log.error("Looks like you forget X or num values")
            api.abort(404, e)

    def _save_model(self, model:Union[DT, LR], id:int):
        models_dao._trained_models[id][self.num] = model
        path = f'./worker/models/model_{self.num}.joblib'
        self._add_to_bd(path, int(id))
        log.info(models_dao._trained_models)

    def _add_to_bd(self, path, id):
        item_doc = {
            'id': self.num,
            'num': id,
            'path': path
            }
        db_model.put(id=int(self.num), data=item_doc)
        log.info(f"Model saved and added to DB {db_model.get(int(models_dao.num))}")
        # log.info(db_model.get(int(models_dao.num)))