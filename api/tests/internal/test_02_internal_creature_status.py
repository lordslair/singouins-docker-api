# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       STATUS_NAME)

def test_singouins_internal_creature_status_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/status/{STATUS_NAME}/30' # PUT
    response  = requests.put(url, headers=HEADERS)
    statuses  = json.loads(response.text)['payload']['statuses']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert statuses[-1]['name']                 == STATUS_NAME

def test_singouins_internal_creature_statuses():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/statuses' # GET
    response  = requests.get(url, headers=HEADERS)
    statuses  = json.loads(response.text)['payload']['statuses']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert statuses[-1]['name']                 == STATUS_NAME

def test_singouins_internal_creature_status_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/status/{STATUS_NAME}' # GET
    response  = requests.get(url, headers=HEADERS)
    status    = json.loads(response.text)['payload']['status']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert status['name']                       == STATUS_NAME

def test_singouins_internal_creature_status_del():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/status/{STATUS_NAME}' # DELETE
    response  = requests.delete(url, headers=HEADERS)
    statuses  = json.loads(response.text)['payload']['statuses']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert statuses                             == []
