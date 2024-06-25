# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    access_token_get,
    )


def test_singouins_action_unload():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons  = json.loads(response.text)['payload']['weapon']
    # We need the Pistolet (metaid:34)
    weapon   = [x for x in weapons if x['metaid'] == 34][0]
    itemid   = weapon['_id']

    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/action/unload/{itemid}',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Unload Query OK' in json.loads(response.text)['msg']
    assert json.loads(response.text)['payload']['weapon']['ammo'] == 0

    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert json.loads(response.text)['payload']['satchel']['ammo']['cal22'] > 0


def test_singouins_action_reload():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons  = json.loads(response.text)['payload']['weapon']
    # We need the Pistolet (metaid:34)
    weapon   = [x for x in weapons if x['metaid'] == 34][0]
    itemid   = weapon['_id']

    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/action/reload/{itemid}',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Reload Query OK' in json.loads(response.text)['msg']
    assert json.loads(response.text)['payload']['weapon']['ammo'] == 6

    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert json.loads(response.text)['payload']['satchel']['ammo']['cal22'] == 0
