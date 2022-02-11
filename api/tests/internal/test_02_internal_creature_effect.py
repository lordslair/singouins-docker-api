# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       EFFECTMETA_ID,
                       HEADERS)

def test_singouins_internal_creature_effects():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effects' # GET
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_effect_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effect/{EFFECTMETA_ID}' # PUT
    payload   = {"duration": 5, "sourceid": 1}
    response  = requests.put(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_effect_get():
    # We grab the first effect id first
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effects' # GET
    response  = requests.get(url, headers=HEADERS)
    effectid  = json.loads(response.text)['payload']['effects'][0]['id']

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effect/{effectid}' # GET
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_effect_del():
    # We grab the first effect id first
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effects' # GET
    response  = requests.get(url, headers=HEADERS)
    effectid  = json.loads(response.text)['payload']['effects'][0]['id']

    # We do the DELETE request
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effect/{effectid}' # DELETE
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
