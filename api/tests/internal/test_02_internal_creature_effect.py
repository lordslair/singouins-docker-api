# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       EFFECT_NAME,
                       EFFECT_JSON,
                       HEADERS)

def test_singouins_internal_creature_effect_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effect/{EFFECT_NAME}' # PUT
    response  = requests.put(url, headers=HEADERS, json = EFFECT_JSON)
    effects   = json.loads(response.text)['payload']['effects']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert effects[-1]['name']                  == EFFECT_NAME

def test_singouins_internal_creature_effects():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effects' # GET
    response  = requests.get(url, headers=HEADERS)
    effects   = json.loads(response.text)['payload']['effects']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert effects[-1]['name']                  == EFFECT_NAME

def test_singouins_internal_creature_effect_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effect/{EFFECT_NAME}' # GET
    response  = requests.get(url, headers=HEADERS)
    effect    = json.loads(response.text)['payload']['effect']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert effect['name']                       == EFFECT_NAME

def test_singouins_internal_creature_effect_del():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/effect/{EFFECT_NAME}' # DELETE
    response  = requests.delete(url, headers=HEADERS)
    effects   = json.loads(response.text)['payload']['effects']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert effects                              == []
