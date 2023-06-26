from flask import Flask, jsonify, request
import time
from celery import Celery
from celery.result import AsyncResult
import asyncio
import json
from WhisperAnalysierWeb import WhisperAnalysier
import os
import random
from typing import List, Union, Optional, Mapping, T

application = Flask(__name__)

REDIS_HOSTS: str = '127.0.0.1'
REDIS_PORT: str = '6379'

application.config['CELERY_BROKER_URL']: str = 'redis://' + REDIS_HOSTS + ':' + REDIS_PORT + '/0'
application.config['CELERY_RESULT_BACKEND']: str = 'redis://' + REDIS_HOSTS + ':' + REDIS_PORT + '/0'

celery = Celery(application.name, broker=application.config['CELERY_BROKER_URL'], backend=application.config['CELERY_RESULT_BACKEND'])
celery.conf.update(application.config)

fila_dowmload_path: str = os.path.abspath("sounds/")

whisper = WhisperAnalysier(model_size="large-v2")
whisper.analyze(path=os.path.abspath("test/test.wav"))

@celery.task
def long_task(name: str) -> str:
    return whisper.analyze(name, remove=True)

@application.route("/get_text_celery", methods=['POST'])
def get_text_celery() -> Mapping[str, str]:
    uploaded_file = request.files['document']
    filename: str = os.path.join(fila_dowmload_path, uploaded_file.filename)
    if uploaded_file.filename != '':
        if os.path.exists(filename):
            rnd: int = random.randint(0, 10000)
            filename = filename[0:-4] +  str(rnd) +  filename[-4:]
        print(filename)
        uploaded_file.save(filename)
    posted_data: Mapping[str, T] = json.load(request.files['datas'])                                                       
    task = long_task.delay(filename)
    res = celery.AsyncResult(task.task_id)
    while not res.ready():
        time.sleep(0.05)
        res = celery.AsyncResult(task.task_id)
    answer: Mapping[str, str] = json.dumps({"answer": res.get()})
    return answer

@application.route("/get_text_process", methods=['POST'])
def get_text_process():
    uploaded_file = request.files['document']
    filename = fila_dowmload_path + uploaded_file.filename
    if uploaded_file.filename != '':
        if os.path.exists(filename):
            rnd = random.randint(0, 10000)
            filename = filename[0:-4] +  str(rnd) +  filename[-4:]
        print(filename)
        uploaded_file.save(filename)
    posted_data = json.load(request.files['datas'])      
    res = whisper.analyze(filename, remove=True)                                              
    answer = json.dumps({"answer": res})
    return answer

if __name__ == "__main__":
    application.run()