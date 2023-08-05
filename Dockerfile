FROM python:3.10-alpine

RUN mkdir app

WORKDIR /app

RUN pip install -r requirements.txt 

COPY . app

VOLUME [ "/data" ]
