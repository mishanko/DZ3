from flask import Flask
from flask_restx import Api
from .ml_models import MLModelsDAO
from .database import Model
from pymongo import MongoClient
from celery import Celery
from config import CELERY_BACKEND, CELERY_BROKER, MONGODB, MONGO_PORT

client = MongoClient(MONGODB, int(MONGO_PORT))
db = client.models
db_model = Model(db)

celery = Celery("train", broker=CELERY_BROKER, backend=CELERY_BACKEND)

models_dao = MLModelsDAO()

application = Flask(__name__)
api = Api(application)

from app import views