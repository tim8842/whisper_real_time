import requests, json, grequests
import asyncio
from flask import jsonify

BASE_URL = "http://127.0.0.1:5000"


# Ton to be sent
datas = {'var1' : 'var1','var2' : 'var2',}

#my file to be sent
local_file_to_send = "14302023113031707A.wav"

url = BASE_URL + "/get_text"

async_url = BASE_URL + "/get_text_async"

files = [
    ('document', (local_file_to_send, open(local_file_to_send, 'rb'), 'application/octet')),
    ('datas', ('datas', json.dumps(datas), 'application/json')),
]

def normal_request():
    r = requests.post(url, files=files)
    print(json.loads(r.content))

def async_request():
    r = grequests.post(url, files=files)
    print("hello")
    r = grequests.map([r])
    print(json.loads(r[0].content))

if __name__ == "__main__":
    async_request()