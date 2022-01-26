# -*- coding: utf8 -*-

import json
import requests

from variables import (API_INTERNAL_TOKEN,
                       API_URL,
                       CREATURE_ID,
                       SKILLMETA_ID)

def test_singouins_internal_creature_cds():
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/cds'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_cd_add():
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}'
    payload   = {"duration": 5}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.put(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_cd_get():
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_cd_del():
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.delete(url, headers=headers)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
