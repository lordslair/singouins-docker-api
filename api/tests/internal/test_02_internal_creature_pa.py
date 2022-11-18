# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_pa_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/pa'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_pa_consume():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/pa/consume/1/1'
    response  = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_pa_reset():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/pa/reset'
    response  = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
