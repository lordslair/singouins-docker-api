# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       SKILLMETA_ID,
                       SKILLMETA_NAME)

def test_singouins_internal_creature_cd_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}' # PUT
    payload   = {"duration": 5}
    response  = requests.put(url, headers=HEADERS, json = payload)
    cds       = json.loads(response.text)['payload']['cds']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert cds[-1]['id']                        == SKILLMETA_ID
    assert cds[-1]['name']['en']                == SKILLMETA_NAME

def test_singouins_internal_creature_cds():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cds' # GET
    response  = requests.get(url, headers=HEADERS)
    cds       = json.loads(response.text)['payload']['cds']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert cds[-1]['id']                        == SKILLMETA_ID
    assert cds[-1]['name']['en']                == SKILLMETA_NAME

def test_singouins_internal_creature_cd_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}' # GET
    response  = requests.get(url, headers=HEADERS)
    cd        = json.loads(response.text)['payload']['cd']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert cd['id']                             == SKILLMETA_ID
    assert cd['name']['en']                     == SKILLMETA_NAME

def test_singouins_internal_creature_cd_del():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILLMETA_ID}' # DELETE
    response  = requests.delete(url, headers=HEADERS)
    cds       = json.loads(response.text)['payload']['cds']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert cds                                  == []
