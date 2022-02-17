# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)

def test_singouins_internal_creature_equipment():
    url       = f'{API_URL}/internal/creature/equipment'
    payload   = {"creatureid": CREATURE_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pa_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/pa'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pa_consume():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/pa/consume/1/1'
    response  = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pa_reset():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/pa/reset'
    response  = requests.post(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_profile():
    url       = f'{API_URL}/internal/creature/profile'
    payload   = {"creatureid": CREATURE_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_stats():
    url       = f'{API_URL}/internal/creature/stats'
    payload   = {"creatureid": CREATURE_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_wallet():
    url       = f'{API_URL}/internal/creature/wallet'
    payload   = {"creatureid": CREATURE_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creatures():
    url       = f'{API_URL}/internal/creatures'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pop():
    url       = f'{API_URL}/internal/creature' # PUT
    payload   = {"raceid": 11,
                 "gender": True,
                 "rarity": "Boss",
                 "instanceid": 0,
                 "x": 3,
                 "y": 3,
                 "m": 121,
                 "r": 122,
                 "g": 123,
                 "v": 124,
                 "p": 125,
                 "b": 126}
    response  = requests.put(url, headers=HEADERS, json = payload)

    creatureid = json.loads(response.text)['payload']['id']

    assert creatureid > 0
    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/creature/{creatureid}' # DELETE
    response  = requests.delete(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
