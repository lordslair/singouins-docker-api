# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       SKILLMETA_ID)

def test_singouins_internal_creature_cds():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cds' # GET
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_cd_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}' # PUT
    payload   = {"duration": 5}
    response  = requests.put(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_cd_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}' # GET
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_cd_del():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}' # DELETE
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
