FROM python:3.8-slim-buster

ENV HOST 0.0.0.0
ENV PORT 8080
ENV CELERY_BROKER redis://redis:6379/0
ENV CELERY_BACKEND redis://redis:6379/0

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080
EXPOSE 5000

CMD ["python", "cli.py"]