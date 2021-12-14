from log import log

class Model:

    def __init__(self, db):
        """Класс базы данных, со всеми операциями CRUD

        Args:
            db ([type]): [description]
        """
        self.models = db.models

    def get(self, id):
        m = self.models.find_one({"id": id})
        return m

    def post(self, data: dict):
        post_id = self.models.insert_one(data).inserted_id
        log.info(post_id)

    def put(self, id: int, data: dict):
        put_id = self.models.update_one({'id': id}, {'$set':data})
        log.info(self.get(id))

    def delete(self, id):
        self.models.delete_one({'id': id})
        log.info("Deleted model: ", id)

    def view_all(self, id):
        d_models = {}
        for i, d in enumerate(self.models.find({"num": id})):
            d_models[i] = str(d)
        return d_models