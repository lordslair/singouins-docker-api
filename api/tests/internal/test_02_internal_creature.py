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

def test_singouins_internal_creature_pa():
    url       = f'{API_URL}/internal/creature/pa'
    payload   = {"creatureid": CREATURE_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pa_reset():
    url       = f'{API_URL}/internal/creature/pa/reset'
    payload   = {"creatureid": CREATURE_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

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

def test_singouins_internal_creature_statuses():
    url       = f'{API_URL}/internal/creature/statuses'
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


    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
