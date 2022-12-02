# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_pop_n_kill():
    url       = f'{API_URL}/internal/creature'  # PUT
    payload   = {"raceid": 11,
                 "gender": True,
                 "rarity": "Boss",
                 "instanceid": 0,
                 "x": 3,
                 "y": 3}
    response  = requests.put(url, headers=HEADERS, json=payload)

    creature = json.loads(response.text)['payload']

    assert creature is not None
    assert creature['id'] is not None
    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True

    url       = f"{API_URL}/internal/creature/{CREATURE_ID}/kill/{creature['id']}" # POST # noqa
    response  = requests.post(url, headers=HEADERS, json=payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True