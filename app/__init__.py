from flask import Flask
from flask_restx import Api
from .ml_models import MLModelsDAO
from celery import Celery
from prometheus_flask_exporter import PrometheusMetrics
from config.config import CELERY_BACKEND, CELERY_BROKER

celery = Celery("train", broker=CELERY_BROKER, backend=CELERY_BACKEND)

models_dao = MLModelsDAO()

application = Flask(__name__)
api = Api(application)
metrics = PrometheusMetrics(application)

from app import views