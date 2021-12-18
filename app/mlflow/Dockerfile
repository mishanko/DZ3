FROM python:3-slim
ARG MLFLOW_VERSION=1.22.0

RUN mkdir -p /usr/src/app/mlflow
WORKDIR /usr/src/app/mlflow
RUN pip install --no-cache-dir mlflow==$MLFLOW_VERSION
EXPOSE 5000

ENV BACKEND_URI sqlite:///mlflow.db
ENV ARTIFACT_ROOT /artifacts
CMD mlflow server --backend-store-uri ${BACKEND_URI} --default-artifact-root ${ARTIFACT_ROOT} --host 0.0.0.0 --port 5000