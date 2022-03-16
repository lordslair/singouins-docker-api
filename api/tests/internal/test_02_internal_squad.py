# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS,
                       SQUAD_ID)

def test_singouins_internal_squad():
    url       = f'{API_URL}/internal/squad'
    payload   = {"squadid": SQUAD_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert json.loads(response.text)['success'] == True
    assert 'Squad Query OK' in json.loads(response.text)['msg']
    assert response.status_code == 200

def test_singouins_internal_squads():
    url       = f'{API_URL}/internal/squads'
    response  = requests.get(url, headers=HEADERS)

    assert json.loads(response.text)['success'] == True
    assert 'Squad Query OK' in json.loads(response.text)['msg']
    assert response.status_code == 200
