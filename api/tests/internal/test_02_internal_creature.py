# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_equipment():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_equipment_ammo_consume():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True

    equipment = json.loads(response.text)['payload']['equipment']
    if equipment['holster'] is not None:
        if equipment['holster']['ammo'] > 0:
            itemid = equipment['holster']['id']
            ammo   = equipment['holster']['ammo']
    elif equipment['righthand'] is not None:
        if equipment['righthand']['ammo'] > 0:
            itemid = equipment['righthand']['id']
            ammo   = equipment['righthand']['ammo']
    elif equipment['lefthand'] is not None:
        if equipment['lefthand']['ammo'] > 0:
            itemid = equipment['lefthand']['id']
            ammo   = equipment['righthand']['ammo']

    assert itemid is not None
    assert ammo   is not None

    if itemid and ammo:
        url = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment/{itemid}/ammo/consume/1'  # noqa
        response = requests.put(url, headers=HEADERS)
        payload  = json.loads(response.text)['payload']

        assert response.status_code                 == 200
        assert json.loads(response.text)['success'] is True
        assert payload['item']['ammo']              == ammo - 1


def test_singouins_internal_creature_equipment_ammo_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True

    equipment = json.loads(response.text)['payload']['equipment']
    if equipment['holster'] is not None:
        if equipment['holster']['ammo'] > 0:
            itemid = equipment['holster']['id']
            ammo   = equipment['holster']['ammo']
    elif equipment['righthand'] is not None:
        if equipment['righthand']['ammo'] > 0:
            itemid = equipment['righthand']['id']
            ammo   = equipment['righthand']['ammo']
    elif equipment['lefthand'] is not None:
        if equipment['lefthand']['ammo'] > 0:
            itemid = equipment['lefthand']['id']
            ammo   = equipment['righthand']['ammo']

    assert itemid is not None
    assert ammo   is not None

    if itemid and ammo:
        url = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment/{itemid}/ammo/add/2'  # noqa
        response = requests.put(url, headers=HEADERS)
        payload = json.loads(response.text)['payload']

        assert response.status_code                 == 200
        assert json.loads(response.text)['success'] is True
        assert payload['item']['ammo']              == ammo + 2


def test_singouins_internal_creature_equipment_ammo_weird():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True

    equipment = json.loads(response.text)['payload']['equipment']
    if equipment['holster'] is not None:
        if equipment['holster']['ammo'] > 0:
            itemid = equipment['holster']['id']
            ammo   = equipment['holster']['ammo']
    elif equipment['righthand'] is not None:
        if equipment['righthand']['ammo'] > 0:
            itemid = equipment['righthand']['id']
            ammo   = equipment['righthand']['ammo']
    elif equipment['lefthand'] is not None:
        if equipment['lefthand']['ammo'] > 0:
            itemid = equipment['lefthand']['id']
            ammo   = equipment['righthand']['ammo']

    assert itemid is not None
    assert ammo   is not None

    if itemid and ammo:
        url = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment/{itemid}/plop/add/2'  # noqa
        response = requests.put(url, headers=HEADERS)

        assert response.status_code                 == 404

        url = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment/{itemid}/ammo/plop/2'  # noqa
        response = requests.put(url, headers=HEADERS)

        assert response.status_code                 == 200
        assert json.loads(response.text)['success'] is False

        url = f'{API_URL}/internal/creature/{CREATURE_ID}/equipment/{itemid}/ammo/add/plop'  # noqa
        response = requests.put(url, headers=HEADERS)

        assert response.status_code                 == 404


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


def test_singouins_internal_creature():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


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


def test_singouins_internal_creature_user():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/user'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']

    assert response.status_code                  == 200
    assert json.loads(response.text)['success']  is True
    assert payload['user']                       is not None
    assert payload['creature']                   is not None
    assert payload['creature']['id']             == CREATURE_ID


def test_singouins_internal_creatures():
    url       = f'{API_URL}/internal/creatures'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_pop_n_kill():
    url       = f'{API_URL}/internal/creature'  # PUT
    payload   = {"raceid": 11,
                 "gender": True,
                 "rarity": "Boss",
                 "instanceid": 0,
                 "x": 3,
                 "y": 3}
    response  = requests.put(url, headers=HEADERS, json=payload)

    creatureid = json.loads(response.text)['payload']['id']

    assert creatureid > 0
    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True

    url       = f'{API_URL}/internal/creature/{creatureid}'  # DELETE
    response  = requests.delete(url, headers=HEADERS, json=payload)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
