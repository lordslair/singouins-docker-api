# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_inventory():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/inventory'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Inventory Query OK' in json.loads(response.text)['msg']
    payload = json.loads(response.text)['payload']
    assert payload['inventory'] is not None
    assert payload['creature']['id'] == CREATURE_ID
