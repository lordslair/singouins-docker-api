# -*- coding: utf8 -*-

import json
import requests

from variables import (API_INTERNAL_TOKEN,
                       API_URL,
                       SQUAD_ID)

def test_singouins_internal_squad():
    url       = API_URL + '/internal/squad'
    payload   = {"squadid": SQUAD_ID}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code == 200

def test_singouins_internal_squads():
    url       = API_URL + '/internal/squads'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
