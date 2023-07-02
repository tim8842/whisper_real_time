from flask import Flask, request
import json
from WhisperAnalysierWeb import WhisperAnalysier
import os
import random
from typing import List, Union, Mapping
import logging
import logging.config
from LoggerConfig import get_logging_dict_config

application = Flask(__name__)

MODEL_SIZE = "large-v2"
TEST_FILE = "test/test.wav"

logging.config.dictConfig(get_logging_dict_config())
logger = logging.getLogger("app.app")

files_download_path: str = os.path.abspath("sounds/")


whisper = WhisperAnalysier(model_size=MODEL_SIZE)
whisper.analyze(path=os.path.abspath(TEST_FILE))

print("test analyze ended.")

started_info: Mapping[str, Union[str, Mapping]] = {
    "WHISPER": {
        "MODEL_SIZE": MODEL_SIZE,
        "TEST_FILE": TEST_FILE
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

@application.route("/get_text_process", methods=['POST'])
def get_text_process():
    request_log(request)
    uploaded_file = request.files['audio']
    uploaded_file.filename = "/" + uploaded_file.filename.split("\\")[-1]
    filename = os.path.join(files_download_path, uploaded_file.filename)
    if uploaded_file.filename != '':
        while os.path.exists(filename):
            rnd = random.randint(0, 10000)
            filename = filename[0:-4] +  str(rnd) +  filename[-4:]
        uploaded_file.save(filename)
        logger.debug(f"route: {request.path}, ip: {request.remote_addr}, saving_file: {filename}")
    # posted_data = json.load(request.files['datas']) 
    logger.debug(f"route: {request.path}, ip: {request.remote_addr} whisper start") 
    res = whisper.analyze(filename, remove=True) 
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