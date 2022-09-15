# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_position():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['id'] == CREATURE_ID

    x = payload['x'] + 1
    y = payload['y'] + 1

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/position/{x}/{y}'
    response  = requests.put(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Position Query OK' in json.loads(response.text)['msg']

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['id'] == CREATURE_ID
    assert payload['x'] == x
    assert payload['y'] == y
