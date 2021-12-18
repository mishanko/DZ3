from celery import Celery
from joblib import dump, load
import mlflow.sklearn
from mlflow.models.signature import infer_signature 
import os
CELERY_BACKEND, CELERY_BROKER, MLFLOW_HOST, MLFLOW_PORT = os.environ['CELERY_BACKEND'], os.environ['CELERY_BROKER'], os.environ['MLFLOW_HOST'], os.environ["MLFLOW_PORT"]

celery = Celery("train", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@celery.task(name='train')
def train(X, y, path):
    model_ = path[9:]
    mlflow.set_tracking_uri(f"http://{MLFLOW_HOST}:{MLFLOW_PORT}/")
    mlflow.set_experiment("classification")
    with mlflow.start_run(run_name='classification_task'):
        clf = load(model_)
        clf.fit(X, y)
        dump(clf, model_)
        mlflow.log_params(clf.get_params())
        mlflow.log_metrics({"train_acc":clf.score(X, y)})
        signature = infer_signature(X, clf.predict(X))
        mlflow.sklearn.log_model(clf, 'skl_model', signature=signature, registered_model_name='trained_model')
    return path