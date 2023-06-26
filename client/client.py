import requests, json
import asyncio
from flask import jsonify
from typing import Mapping, List
import os

BASE_URL = "http://127.0.0.1:5000"


# Ton to be sent
# datas: Mapping[str, str] = {'var1' : 'var1','var2' : 'var2',}

# #my file to be sent
# local_file_to_send: str = "14302023113031707A.wav"

# url: str = BASE_URL + "/get_text_celery"
# print(url)


# files:List[tuple] = [
#     ('document', (local_file_to_send, open(local_file_to_send, 'rb'), 'application/octet')),
#     ('datas', ('datas', json.dumps(datas), 'application/json')),
# ]

def normal_request(ulr: str, files: List[tuple]) -> None:
    r = requests.post(url, files=files)
    print(json.loads(r.content))

# def async_request() -> None:
#     r = grequests.post(url, files=files)
#     print("hello")
#     r = grequests.map([r])
#     print(json.loads(r[0].content))

if __name__ == "__main__":
 

    directory = "3515"
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f) and filename.endswith('.wav'):
            print(f)
            datas: Mapping[str, str] = {'var1' : 'var1','var2' : 'var2',}

            local_file_to_send: str = f

            url: str = BASE_URL + "/get_text_process"
            print(url)
            files:List[tuple] = [
                ('document', (local_file_to_send, open(local_file_to_send, 'rb'), 'application/octet')),
                ('datas', ('datas', json.dumps(datas), 'application/json')),
            ]
            normal_request(url, files)