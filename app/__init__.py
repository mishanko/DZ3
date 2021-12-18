from flask import Flask
from flask_restx import Api
from .ml_models import MLModelsDAO
from prometheus_flask_exporter import PrometheusMetrics

models_dao = MLModelsDAO()

application = Flask(__name__)
api = Api(application)
metrics = PrometheusMetrics(application)

from app import views