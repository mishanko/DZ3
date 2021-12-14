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
        log.info("Posted a model under {post_id} ID")

    def put(self, id: int, data: dict):
        self.models.update_one({'id': id}, {'$set':data})
        log.info(f"Model's ID in DB: {self.get(id)}")

    def delete(self, id):
        self.models.delete_one({'id': id})
        log.info("Deleted model's ID: {id}")

    def view_all(self, id):
        d_models = {}
        for i, d in enumerate(self.models.find({"num": id})):
            d_models[i] = str(d)
        return d_models