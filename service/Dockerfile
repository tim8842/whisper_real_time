FROM nvidia/cuda:11.2.1-runtime-ubi8
FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY . .
WORKDIR .
RUN pip install -r requirements.txt
