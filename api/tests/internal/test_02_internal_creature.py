# -*- coding: utf8 -*-

import json
import requests

from variables import (API_INTERNAL_TOKEN,
                       API_URL)

def test_singouins_internal_creature_cds():
    url       = API_URL + '/internal/creature/cds'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_equipment():
    url       = API_URL + '/internal/creature/equipment'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pa():
    url       = API_URL + '/internal/creature/pa'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_pa_reset():
    url       = API_URL + '/internal/creature/pa/reset'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_profile():
    url       = API_URL + '/internal/creature/profile'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_stats():
    url       = API_URL + '/internal/creature/stats'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_statuses():
    url       = API_URL + '/internal/creature/statuses'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_internal_creature_wallet():
    url       = API_URL + '/internal/creature/wallet'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] == True
