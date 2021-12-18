FROM python:3.8-slim-buster

ENV HOST 0.0.0.0
ENV PORT 8080
ENV MLFLOW_HOST 0.0.0.0
ENV MLFLOW_PORT 5000

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

RUN apt-get update && apt-get upgrade -y && apt-get install -y git
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "cli.py"]