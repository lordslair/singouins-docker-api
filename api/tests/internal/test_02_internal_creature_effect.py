# -*- coding: utf8 -*-

import json
import requests

from variables import (API_INTERNAL_TOKEN,
                       API_URL,
                       CREATURE_ID,
                       EFFECTMETA_ID)

def test_singouins_internal_creature_effects():
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/effects'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_effect_add():
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/effect/{EFFECTMETA_ID}'
    payload   = {"duration": 5, "sourceid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.put(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_effect_get():
    # We grab the first effect id first
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/effects'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)
    effectid  = json.loads(response.text)['payload']['effects'][0]['id']

    url       = API_URL + f'/internal/creature/{CREATURE_ID}/effect/{effectid}'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_effect_del():
    # We grab the first effect id first
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/effects'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)
    effectid  = json.loads(response.text)['payload']['effects'][0]['id']

    # We do the DELETE request
    url       = API_URL + f'/internal/creature/{CREATURE_ID}/effect/{effectid}'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.delete(url, headers=headers)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
