# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_wallet():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['wallet']['ammo']['cal50']   >= 0


def test_singouins_internal_creature_wallet_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']
    cal50     = payload['wallet']['ammo']['cal50']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['wallet']['ammo']['cal50']   >= 0

    url = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet/cal50/add/30'
    response = requests.put(url, headers=HEADERS)
    payload = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['wallet']['ammo']['cal50']   == cal50 + 30


def test_singouins_internal_creature_wallet_consume():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']
    cal50     = payload['wallet']['ammo']['cal50']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['wallet']['ammo']['cal50']   >= 0

    url = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet/cal50/consume/25'
    response = requests.put(url, headers=HEADERS)
    payload = json.loads(response.text)['payload']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert payload['wallet']['ammo']['cal50']   == cal50 - 25


def test_singouins_internal_creature_wallet_weird():
    url = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet/cal50/plop/30'
    response = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is False

    url = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet/plip/add/30'
    response = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is False

    url = f'{API_URL}/internal/creature/{CREATURE_ID}/wallet/plip/add/plop'
    response = requests.put(url, headers=HEADERS)

    assert response.status_code                 == 404
