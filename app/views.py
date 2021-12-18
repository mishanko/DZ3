from app import api, models_dao, celery, metrics
from joblib import dump, load
from log import log

from typing import Tuple, Union, NoReturn
from flask_restx import Resource
from sklearn.linear_model import LogisticRegression as LR
from sklearn.tree import DecisionTreeClassifier as DT
import numpy as np
import os


# * Словарь моделей, доступных для обучения
models = {
    1:LR,
    2:DT
    }

@api.route('/api/ml_models')
class MLModels(Resource):
    """Класс для отображения списка доступных для обучения моделей
       и гиперпараметров
    """
    
    @metrics.counter('cnt_gets_models', 'Number_of_gets', labels={'status': lambda resp:resp.status_code})
    def get(self) -> list:
        log.info(f'Trained models = {models_dao._trained_models}')
        return models_dao._ml_models


@api.route('/api/ml_models/<int:id>')
class MLModel(Resource): 
    """Класс для отображения конкретной модели
       и её гиперпараметров
    """
    
    @metrics.counter(f'cnt_gets', 'Number_of_gets', labels={'status': lambda resp:resp.status_code})
    def get(self, id:int) -> Union[Tuple[dict, dict], NoReturn]:
        try:
            name = models_dao._ml_models[id-1]["name"]
            trained = models_dao._ml_models[id-1]["trained"]
            log.info(f'MODEL id = {id} CLASS = {name} TRAINED = {trained}')
            model = models_dao._ml_models[id-1]
            return model, 200
        except IndexError:
            log.warning("Entered invalid model ID")
            # api.abort(404, e)


@api.route('/api/ml_models/<int:id>/train')
class MLModelTrain(Resource): 
    """Класс для обучения
    """
    
    @metrics.counter(f'cnt_trains', 'Number_of_puts', labels={'status': lambda resp:resp.status_code})
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

            import mlflow
            mlflow.set_tracking_uri('http://localhost:5000')
            client = mlflow.tracking.MlflowClient()
            client.create_experiment('classification')
            # посылаем в контейнер для обучения
            celery.send_task("train", args=[X, y, path])
            
            log.info("Training finished!")
            return path
        except KeyError or AttributeError:
            log.warning("Looks like you either forget X or y values")
            # api.abort(404, e)

    def _save_model(self, model:Union[DT, LR], id:int):
        log.info(f"Saving the model...")
        models_dao._trained_models[id][str(models_dao.num)] = model
        models_dao.num += 1


@api.route('/api/ml_models/<int:id>/predict')
class MLModelPredict(Resource): 
    """Класс для предсказания
    """
    
    @metrics.counter(f'cnt_predicts', 'Number_of_predicts', labels={'status': lambda resp:resp.status_code})
    def post(self, id:int) -> Tuple[dict, int]: 
        prediction = self._predict()
        log.info(f"Here is the prediction: {prediction} for {id}")
        return prediction, 200

    def _predict(self) -> Union[dict, NoReturn]:
        try:
            df = api.payload
            number = df['num']
            path = f'./worker/models/model_{number}.joblib'
            model = load(path)
            X_new = np.fromiter(df['X'], dtype=float)
            prediction = {'Prediction': str(model.predict([X_new]))}
            return prediction
        except KeyError:
            log.warning("Invalid model number or No trained models")
            # api.abort(404, e)


@api.route('/api/ml_models/<int:id>/delete')
class MLModelDelete(Resource): 
    """Класс для удаления
    """
    @metrics.counter(f'cnt_deletes', 'Number_of_deletes', labels={'status': lambda resp:resp.status_code})
    def delete(self, id:int) -> Union[Tuple[str, int], NoReturn]:
        try: 
            df = api.payload
            num = df['num']
            models_dao.delete(id, num)
            path = f'./worker/models/model_{num}.joblib'
            os.system(f"rm -rf {path}")
            log.info(f"Model {num} deleted")
            return '', 204
        except KeyError:
            log.warning("Invalid model number")
            # api.abort(404, e)


@api.route('/api/ml_models/<int:id>/retrain')
class MLModelRetrain(MLModelTrain): 
    """Класс для переобучения модели
    """

    @metrics.counter(f'cnt_retrains', 'Number_of_puts', labels={'status': lambda resp:resp.status_code})
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
            log.info("Start retraining")
            
            path = f'./worker/models/model_{self.num}.joblib'
            dump(model, path)

            # посылаем в контейнер для обучения
            celery.send_task("train", args=[X, y, path])
            
            log.info("Retraining finished!")
            return path
        except KeyError:
            log.warning("Looks like you forget X or num values")
            # api.abort(404, e)

    def _save_model(self, model:Union[DT, LR], id:int):
        log.info(f"Saving the model...")
        models_dao._trained_models[id][self.num] = model