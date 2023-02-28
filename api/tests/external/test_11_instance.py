# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       AUTH_PAYLOAD,
                       CREATURE_ID,
                       CREATURE_NAME,
                       )


def test_singouins_mypc_instance_create():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc/{CREATURE_ID}/instance'  # PUT
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
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    url      = f"{API_URL}/mypc/{CREATURE_ID}/instance/{pc['instance']}"  # GET
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
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    url      = f"{API_URL}/mypc/{CREATURE_ID}/instance/{pc['instance']}/leave"  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_join():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert pc['instance'] is None

    # We create a PJTestInstanceJoin
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
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTestInstanceJoin)
    target   = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    # PJTestInstanceJoin creates an instance
    url      = f"{API_URL}/mypc/{target['id']}/instance"  # PUT
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
    url      = f'{API_URL}/mypc/{CREATURE_ID}/instance/{instanceid}/join'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    # We check that we are linked in the instance
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]
    pcjoin   = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert pc['instance'] == instanceid
    assert pcjoin['instance'] == instanceid

    # We leave the instance with PJTest
    url      = f"{API_URL}/mypc/{CREATURE_ID}/instance/{instanceid}/leave"  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    # We check that we are not linked in the instance anymore
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]
    pcjoin   = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert pc['instance'] is None
    assert pcjoin['instance'] == instanceid
