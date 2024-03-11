# -*- coding: utf8 -*-

import json
import requests

from variables import (
    AUTH_PAYLOAD,
    API_URL,
    CREATURE_ID,
    )


def test_singouins_profession_recycling():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url        = f'{API_URL}/mypc/{CREATURE_ID}/item'  # GET
    response   = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons    = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster (bc of precedent tests on items)
    holster    = json.loads(response.text)['payload']['equipment']['holster']
    # So we need the other one
    weapon     = [x for x in weapons if x['id'] != holster][0]
    itemuuid   = weapon['id']

    url        = f'{API_URL}/mypc/{CREATURE_ID}/action/profession/skinning/{itemuuid}'  # POST
    response   = requests.post(url, headers=headers)
    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
