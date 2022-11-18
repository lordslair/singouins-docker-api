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
