# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID


def test_singouins_action_unload(jwt_header, myitems):
    weapon   = [x for x in myitems['weapon'] if x['metaid'] == 34][0]
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/action/unload/{weapon['_id']}", headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Unload Query OK' in response.json().get("msg")
    assert response.json().get("payload")['weapon']['ammo'] == 0

    response = requests.get(f'{API_URL}/mypc/{CREATURE_ID}/item', headers=jwt_header['access'])

    assert response.status_code == 200
    assert response.json().get("success") is True
    assert response.json().get("payload")['satchel']['ammo']['cal22'] > 0


def test_singouins_action_reload(jwt_header, myitems):
    weapon   = [x for x in myitems['weapon'] if x['metaid'] == 34][0]
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/action/reload/{weapon['_id']}", headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Reload Query OK' in response.json().get("msg")
    assert response.json().get("payload")['weapon']['ammo'] == 6

    response = requests.get(f'{API_URL}/mypc/{CREATURE_ID}/item', headers=jwt_header['access'])

    assert response.status_code == 200
    assert response.json().get("success") is True
    assert response.json().get("payload")['satchel']['ammo']['cal22'] == 0
