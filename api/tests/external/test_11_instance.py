# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    CREATURE_NAME,
    access_token_get,
    )

PJTEST_BODY = {
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


def test_singouins_mypc_instance_create():
    response  = requests.put(
        f'{API_URL}/mypc/{CREATURE_ID}/instance',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json={"mapid": 1, "hardcore": True, "fast": False, "public": True}
        )

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_get():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    response = requests.get(
        f"{API_URL}/mypc/{CREATURE_ID}/instance/{pc['instance']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_leave():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/instance/{pc['instance']}/leave",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_instance_join():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'instance' not in pc

    # We create a PJTestInstanceJoin
    response = requests.post(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json=PJTEST_BODY,
        )

    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTestInstanceJoin)
    target = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    # PJTestInstanceJoin creates an instance
    response  = requests.put(
        f"{API_URL}/mypc/{target['_id']}/instance",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json={"mapid": 1, "hardcore": True, "fast": False, "public": True}
        )

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True

    instanceid = json.loads(response.text)['payload']['_id']
    assert instanceid is not None

    # We join PJTestInstanceJoin instance
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/instance/{instanceid}/join",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    # We check that we are linked in the instance
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]
    pcjoin = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert pc['instance'] == instanceid
    assert pcjoin['instance'] == instanceid

    # We leave the instance with PJTest
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/instance/{instanceid}/leave",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    # We check that we are not linked in the instance anymore
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]
    pcjoin = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'instance' not in pc
    assert pcjoin['instance'] == instanceid
