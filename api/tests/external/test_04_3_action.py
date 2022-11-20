# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       CREATURE_ID,
                       )


def test_singouins_action_unload():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/item'  # GET
    response = requests.get(url, headers=headers)
    weapons  = json.loads(response.text)['payload']['weapon']
    # We need the Pistolet (metaid:34)
    weapon   = [x for x in weapons if x['metaid'] == 34][0]
    itemid   = weapon['id']

    url       = f'{API_URL}/mypc/{CREATURE_ID}/action/unload/{itemid}'  # POST
    response  = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Unload Query OK' in json.loads(response.text)['msg']
    assert json.loads(response.text)['payload']['weapon']['ammo'] == 0

    url        = f'{API_URL}/mypc/{CREATURE_ID}/item'  # GET
    response   = requests.get(url, headers=headers)
    wallet     = json.loads(response.text)['payload']['wallet']

    assert wallet['ammo']['cal22'] > 0


def test_singouins_action_reload():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/item'  # GET
    response = requests.get(url, headers=headers)
    weapons  = json.loads(response.text)['payload']['weapon']
    # We need the Pistolet (metaid:34)
    weapon   = [x for x in weapons if x['metaid'] == 34][0]
    itemid   = weapon['id']

    url       = f'{API_URL}/mypc/{CREATURE_ID}/action/reload/{itemid}'  # POST
    response  = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Reload Query OK' in json.loads(response.text)['msg']
    assert json.loads(response.text)['payload']['weapon']['ammo'] == 6

    url        = f'{API_URL}/mypc/{CREATURE_ID}/item'  # GET
    response   = requests.get(url, headers=headers)
    wallet     = json.loads(response.text)['payload']['wallet']

    assert wallet['ammo']['cal22'] == 0
