# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_item_add_n_del():
    ITEM_JSON = {
        "metatype": 'weapon',
        "metaid": 23,
        "rarity": 'Legendary',
        }

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/item'
    response  = requests.put(url, headers=HEADERS, json=ITEM_JSON)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True
    assert 'Item Query OK' in json.loads(response.text)['msg']
    payload = json.loads(response.text)['payload']
    assert payload['item'] is not None
    assert payload['item']['metaid'] == 23
    assert payload['item']['rarity'] == 'Legendary'
    assert payload['creature']['id'] == CREATURE_ID

    itemid    = payload['item']['id']
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/item/{itemid}'
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Item Query OK' in json.loads(response.text)['msg']
