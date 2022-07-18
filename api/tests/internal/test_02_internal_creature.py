# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)

def test_singouins_internal_creature_equipment():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment'
    response  = requests.get(url, headers=HEADERS)

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
    response  = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_stats():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/stats'
    response  = requests.get(url, headers=HEADERS)
    stats     = json.loads(response.text)['payload']['stats']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
    assert stats['def']['hp']                   <= stats['def']['hpmax']

def test_singouins_internal_creature_wallet():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet'
    response  = requests.get(url, headers=HEADERS)

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
                 "y": 3}
    response  = requests.put(url, headers=HEADERS, json = payload)

    creatureid = json.loads(response.text)['payload']['id']

    assert creatureid > 0
    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/creature/{creatureid}' # DELETE
    response  = requests.delete(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
