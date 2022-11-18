# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_stats():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/stats'
    response  = requests.get(url, headers=HEADERS)
    stats     = json.loads(response.text)['payload']['stats']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert stats['def']['hp']                   <= stats['def']['hpmax']


def test_singouins_internal_creature_stats_hp_consume():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/stats'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True

    hp = json.loads(response.text)['payload']['stats']['def']['hp']

    url = f'{API_URL}/internal/creature/{CREATURE_ID}/stats/hp/consume/30'
    response = requests.put(url, headers=HEADERS)
    payload = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['stats']['def']['hp']        == hp - 30


def test_singouins_internal_creature_stats_hp_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/stats'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True

    hp = json.loads(response.text)['payload']['stats']['def']['hp']

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/stats/hp/add/20'
    response  = requests.put(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['stats']['def']['hp']        == hp + 20
