# -*- coding: utf8 -*-

import json
import requests

from variables import *

def test_singouins_internal_korp():
    url       = API_URL + '/internal/korp'
    payload   = {"korpid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code == 200

def test_singouins_internal_korps():
    url       = API_URL + '/internal/korps'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
