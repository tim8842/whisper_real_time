from flask import Flask, jsonify, request
import time
from celery import Celery
from celery.result import AsyncResult
import json
from WhisperAnalysierWeb import WhisperAnalysier
import os
import random
from typing import List, Union, Optional, Mapping, T
import logging
import logging.config
from LoggerConfig import get_logging_dict_config

application = Flask(__name__)

REDIS_HOSTS: str = '127.0.0.1'
REDIS_PORT: str = '6379'

MODEL_SIZE = "large-v2"
TEST_FILE = "test/test.wav"

application.config['CELERY_BROKER_URL']: str = 'redis://' + REDIS_HOSTS + ':' + REDIS_PORT + '/0'
application.config['CELERY_RESULT_BACKEND']: str = 'redis://' + REDIS_HOSTS + ':' + REDIS_PORT + '/0'

logging.config.dictConfig(get_logging_dict_config())
logger = logging.getLogger("app.app")

celery = Celery(application.name, broker=application.config['CELERY_BROKER_URL'], backend=application.config['CELERY_RESULT_BACKEND'])
celery.conf.update(application.config)

files_download_path: str = os.path.abspath("sounds/")


whisper = WhisperAnalysier(model_size=MODEL_SIZE)
whisper.analyze(path=os.path.abspath(TEST_FILE))

started_info: Mapping[str, Union[str, Mapping]] = {
    "WHISPER": {
        "MODEL_SIZE": MODEL_SIZE,
        "TEST_FILE": TEST_FILE
    },
    "REDIS": {
        "HOST": REDIS_HOSTS, "PORT": REDIS_PORT
    }, 
    "CELERY": {
        "CELERY_BROKER_URL": application.config['CELERY_BROKER_URL'],
        "CELERY_RESULT_BACKEND": application.config['CELERY_RESULT_BACKEND']
    },
    "FILES_DOWNLOAD_PATH": files_download_path
}

def request_log(request):
    logger.debug({"request": {
        "route": request.path,
        "ip": request.remote_addr,
        "method": request.method,
        "data": request.data,
        "files": request.files,
        }
    })

@celery.task
def long_task(name: str) -> str:
    return whisper.analyze(name, remove=True, no_speech_prob=0.6)

@application.route("/get_text_celery", methods=['POST'])
def get_text_celery() -> Mapping[str, str]:
    request_log(request)
    uploaded_file = request.files['audio']
    uploaded_file.filename = "/" + uploaded_file.filename.split("\\")[-1]
    filename: str = os.path.join(files_download_path, uploaded_file.filename)
    if uploaded_file.filename != '':
        if os.path.exists(filename):
            rnd: int = random.randint(0, 10000)
            filename = filename[0:-4] +  str(rnd) +  filename[-4:]
        uploaded_file.save(filename)
        logger.debug(f"route: {request.path}, ip: {request.remote_addr}, saving_file: {filename}")
    # posted_data: Mapping[str, T] = json.load(request.files['datas'])                                                      
    task = long_task.delay(filename)
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} whisper celery start: task_id = {task.task_id}")  
    res = celery.AsyncResult(task.task_id)
    while not res.ready():
        time.sleep(0.05)
        res = celery.AsyncResult(task.task_id)
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} whisper celery end: task_id = {task.task_id}")  
    answer = json.dumps({"answer": res.get()})
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} request end, result: {json.loads(answer)}")  
    return answer

@application.route("/get_text_process", methods=['POST'])
def get_text_process():
    request_log(request)
    uploaded_file = request.files['audio']
    uploaded_file.filename = "/" + uploaded_file.filename.split("\\")[-1]
    filename = files_download_path + uploaded_file.filename
    print(uploaded_file.filename)
    print(filename)
    if uploaded_file.filename != '':
        if os.path.exists(filename):
            rnd = random.randint(0, 10000)
            filename = filename[0:-4] +  str(rnd) +  filename[-4:]
        uploaded_file.save(filename)
        logger.debug(f"route: {request.path}, ip: {request.remote_addr}, saving_file: {filename}")
    # posted_data = json.load(request.files['datas']) 
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} whisper start") 
    res = whisper.analyze(filename, remove=True, no_speech_prob=0.6) 
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} whisper end")                                              
    answer = json.dumps({"answer": res})
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} request end, result: {json.loads(answer)}")   
    return answer

@application.route("/test", methods=['POST'])
def get_test():
    request_log(request)
    return {"answer": "hello"}

if __name__ == "__main__":
    logger.debug("logger was initialized")
    logger.debug(started_info)
    application.run(debug=False, host="0.0.0.0")