# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       AUTH_PAYLOAD)


def test_singouins_mypc_instance_create():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)

    pcid       = json.loads(response.text)['payload'][0]['id']

    assert json.loads(response.text)['payload'][0]['instance'] is None

    url      = f'{API_URL}/mypc/{pcid}/instance'  # PUT
    payload  = {"mapid": 1,
                "hardcore": True,
                "fast": False,
                "public": True}
    response = requests.put(url, json=payload, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_get():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)

    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_leave():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)

    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}/leave'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_join():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url        = f'{API_URL}/mypc'  # GET
    response   = requests.get(url, headers=headers)
    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert instanceid is None

    # We create a PJTestSquadKick
    url = f'{API_URL}/mypc'  # POST
    payload_c = {
        'name': 'PJTestInstanceJoin',
        'gender': True,
        'race': 2,
        'class': 3,
        'cosmetic': {
            'metaid': 8,
            'data': {
                'hasGender': True,
                'beforeArmor': False,
                'hideArmor': None,
            },
        },
        'equipment': {
            'righthand': {
                'metaid': 34,
                'metatype': 'weapon',
            },
            'lefthand': {
                'metaid': 11,
                'metatype': 'weapon'
            }
        }
    }
    response = requests.post(url, json=payload_c, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # PJTestInstanceJoin creates an instance
    url      = f'{API_URL}/mypc/{targetid}/instance'  # PUT
    payload  = {"mapid": 1,
                "hardcore": True,
                "fast": False,
                "public": True}
    response = requests.put(url, json=payload, headers=headers)

    instanceid = json.loads(response.text)['payload']['id']

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True
    assert instanceid is not None

    # We join PJTestInstanceJoin instance
    url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}/join'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    # We check that we are linked in the instance
    url        = f'{API_URL}/mypc'  # GET
    response   = requests.get(url, headers=headers)
    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert instanceid is not None

    url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}/leave'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
