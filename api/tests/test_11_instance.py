# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID, CREATURE_NAME, PJTEST_BODY


def test_singouins_mypc_instance_create(jwt_header):
    BODY = {"mapid": 1, "hardcore": True, "fast": False, "public": True}
    response  = requests.put(f'{API_URL}/mypc/{CREATURE_ID}/instance', headers=jwt_header['access'], json=BODY)  # noqa: E501
    assert response.status_code == 201
    assert response.json().get("success") is True


def test_singouins_mypc_instance_get(jwt_header, mypc):
    instance_id = mypc['indexed'][CREATURE_ID]['instance']

    response = requests.get(f"{API_URL}/mypc/{CREATURE_ID}/instance/{instance_id}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_mypc_instance_leave(jwt_header, mypc):
    instance_id = mypc['indexed'][CREATURE_ID]['instance']

    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/instance/{instance_id}/leave", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_mypc_instance_join(jwt_header, mypc):
    assert 'instance' not in mypc['indexed'][CREATURE_ID]

    # We create a PJTestInstanceJoin
    PJTEST_BODY['name'] = 'PJTestInstanceJoin'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])
    pcs = response.json().get("payload")
    # We need the PC (name:PJTestInstanceJoin)
    target = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    # PJTestInstanceJoin creates an instance
    BODY = {"mapid": 1, "hardcore": True, "fast": False, "public": True}
    response  = requests.put(f"{API_URL}/mypc/{target['_id']}/instance", headers=jwt_header['access'], json=BODY)  # noqa: E501
    assert response.status_code == 201
    assert response.json().get("success") is True

    instance_id = response.json().get("payload")['_id']

    # We join PJTestInstanceJoin instance
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/instance/{instance_id}/join", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True

    # We check that we are linked in the instance
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])
    pcs = response.json().get("payload")
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]
    pcjoin = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    assert response.status_code == 200
    assert response.json().get("success") is True
    assert pc['instance'] == instance_id
    assert pcjoin['instance'] == instance_id

    # We leave the instance with PJTest
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/instance/{instance_id}/leave", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True

    # We check that we are not linked in the instance anymore
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])
    pcs = response.json().get("payload")
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]
    pcjoin = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]

    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'instance' not in pc
    assert pcjoin['instance'] == instance_id
