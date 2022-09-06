# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       AUTH_PAYLOAD,
                       CREATURE_ID)


def test_singouins_public_pc():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    pcid      = CREATURE_ID
    url       = f'{API_URL}/pc/{pcid}'  # GET
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_public_pc_events():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    pcid      = CREATURE_ID
    url       = f'{API_URL}/pc/{pcid}/event'  # GET
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_public_pc_item():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    pcid      = CREATURE_ID
    url       = f'{API_URL}/pc/{pcid}/item'  # GET
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
