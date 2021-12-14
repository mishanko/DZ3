from typing import Tuple, Union, NoReturn
from log import log

class MLModelsDAO:
    """В этом классе реализуем CRUD"""
    
    def __init__(self):

        # индекс обученных моделей
        self.num = 0

        # словарь обученных моделей
        self._trained_models = {1: {},
                                2: {}}

        # словарь доступных для обучения моделей и их гиперпараметры
        self._ml_models = ({'id':1, 'name':'logreg', 'hyperparameters':{"max_iter":"int",
                                                                        "penalty":["l1", "l2", "elasticnet"],
                                                                        "tol":"float",
                                                                        "C":"float",
                                                                        "solver":["newton-cg", "lbfgs", "liblinear", "sag", "saga"]
                                                                        },
                                                                        'trained':False}, 
                           {'id':2, 'name':'tree', 'hyperparameters':{"criterion":["gini", "entropy"],
                                                                      "splitter":["best", "random"],
                                                                      "max_depth":"int",
                                                                      "min_samples_split":"int or float",
                                                                      "min_samples_leaf":"int or float",
                                                                      "min_weight_fraction_leaf": "float",
                                                                      "max_features":"int or float or [auto, sqrt, log2]",
                                                                      }, 
                                                                      'trained':False})


    def get(self, id:int) -> Union[Tuple[dict, dict], NoReturn]:
        """Функция для получения информации о моделях

        Args:
            id (int): ID модели

        Raises:
            e: Ошибка на неналичие ID

        Returns:
            Union[Tuple[dict, dict], NoReturn]: Информация о моделях и словарь обученных моделей
        """
        try:
            res = list(filter(lambda x: x['id']==id, self._ml_models)) # поиск модели по ID
            trained_models = self._trained_models
            return (res[0], '{}'.format(trained_models))# 0 так как возвращается список
        except NotImplementedError as e:
            log.error('ml_model {} does not exist'.format(id))
            raise e('ml_model {} does not exist'.format(id))

    def update(self, id:int, data:dict) -> dict:
        """Обновление информации о моделях

        Args:
            id (int): ID модели
            data (dict): Словарь для изменения данных

        Returns:
            dict: Измененная модель
        """
        ml_model = self.get(id)[0] 
        ml_model.update(data)
        return ml_model

    def delete(self, id:int, num:str):
        """Удаление обученной модели

        Args:
            id (int): ID модели
            num (str): Номер обученной модели
        """
        self._trained_models[id][num] = None # удаление происходит заменой на None
        self._check_for_empty(id)
        self.get(id)[1]
    
    def _check_for_empty(self, id:int):
        """Вспомогательная функция, для смены статуса trained
        
        Args:
            id (int): ID модели
        """
        for model in self._trained_models[id].values():
            if model is not None:
                return
        data = {'trained': False}
        self.update(id, data)
