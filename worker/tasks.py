from celery import Celery
import os
from joblib import dump
import joblib

CELERY_BROKER = os.environ["CELERY_BROKER"]
CELERY_BACKEND = os.environ["CELERY_BACKEND"]
celery = Celery("train", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@celery.task(name='train')
def train(X, y, path):
    model_ = path[9:]
    clf = joblib.load(model_)
    print(clf, type(clf))
    clf.fit(X, y)
    dump(clf, model_)
    return path