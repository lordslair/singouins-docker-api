# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_auction_sell():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    response  = requests.put(url, headers=HEADERS, json={'price': 100, 'duration': 500})

    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_remove():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_resell():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    response  = requests.put(url, headers=HEADERS, json={'price': 100, 'duration': 500})

    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_buy():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    response  = requests.post(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_reremove():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
