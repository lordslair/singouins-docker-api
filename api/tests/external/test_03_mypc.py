# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       CREATURE_ID,
                       CREATURE_NAME)


def test_singouins_mypc_create():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}
    payload     = {
        'name': CREATURE_NAME,
        'gender': True,
        'race': 2,
        'class': 3,
        'cosmetic': {
            'metaid': 8,
            'data': {
                'hasGender': True,
                'beforeArmor': False,
                'hideArmor': None,
            }
        },
        'equipment': {
            'righthand': {
                'metaid': 34,
                'metatype': 'weapon'
            },
            'lefthand': {
                'metaid': 11,
                'metatype': 'weapon'
            }
        }
    }

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_infos():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcname   = json.loads(response.text)['payload'][0]['name']

    assert pcname == CREATURE_NAME
    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_view():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/view'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_stats():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/stats'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_effects():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/effects'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    payload = json.loads(response.text)['payload']
    assert isinstance(payload['effects'], list)


def test_singouins_mypc_cds():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/cds'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    payload = json.loads(response.text)['payload']
    assert isinstance(payload['cds'], list)


def test_singouins_mypc_statuses():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/statuses'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    payload = json.loads(response.text)['payload']
    assert isinstance(payload['statuses'], list)
