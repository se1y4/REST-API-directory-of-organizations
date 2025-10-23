FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./gunicorn_conf.py /app/

COPY ./app /app/app

COPY ./config.yaml /app/config.yaml
ENV PYTHONPATH="/app:${PYTHONPATH}"