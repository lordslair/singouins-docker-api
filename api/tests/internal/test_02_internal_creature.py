# -*- coding: utf8 -*-

import json
import requests

from variables import API_URL, CREATURE_NAME, HEADERS


def test_singouins_internal_creatures():
    url       = f'{API_URL}/internal/creatures'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature():
    url       = f'{API_URL}/internal/creatures'
    response  = requests.get(url, headers=HEADERS)
    pcs       = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc        = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    url       = f"{API_URL}/internal/creature/{pc['id']}"
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_pop_n_delete():
    url       = f'{API_URL}/internal/creature'  # PUT
    payload   = {"raceid": 11,
                 "gender": True,
                 "rarity": "Boss",
                 "instanceid": None,
                 "x": 3,
                 "y": 3}
    response  = requests.put(url, headers=HEADERS, json=payload)

    creature = json.loads(response.text)['payload']

    assert creature is not None
    assert creature['id'] is not None
    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True

    url       = f"{API_URL}/internal/creature/{creature['id']}"  # DELETE
    response  = requests.delete(url, headers=HEADERS, json=payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
