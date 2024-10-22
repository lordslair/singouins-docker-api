# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID, PJTEST_BODY


def test_singouins_korp_create(jwt_header):
    response = requests.post(f'{API_URL}/mypc/{CREATURE_ID}/korp', headers=jwt_header['access'], json={"name": 'KorpTest'})  # noqa: E501

    assert response.status_code == 201
    assert response.json().get("success") is True
    assert 'Korp create OK' in response.json().get("msg")


def test_singouins_korp_get(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    response = requests.get(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}", headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    members = response.json().get("payload")['members']
    # We need the PC (name:PJTest)
    pc  = [x for x in members if x['name'] == 'PJTest'][0]
    assert pc['korp']['rank'] == 'Leader'
    assert 'Korp Query OK' in response.json().get("msg")


def test_singouins_korp_invite(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    # We create a PJTestKorpInvite
    PJTEST_BODY['name'] = 'PJTestKorpInvite'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestKorpInvite)
    target = [x for x in pcs if x['name'] == 'PJTestKorpInvite'][0]

    # We invite PJTestKorpInvite
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp invite OK' in response.json().get("msg")

    # We cleanup the PJTestKorpInvite
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_korp_kick(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    # We create a PJTestKorpKick
    PJTEST_BODY['name'] = 'PJTestKorpInvite'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestKorpInvite)
    target = [x for x in pcs if x['name'] == 'PJTestKorpInvite'][0]

    # We invite PJTestKorpKick
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp invite OK' in response.json().get("msg")

    # We kick PJTestKorpKick
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}/kick/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp kick OK' in response.json().get("msg")

    # We cleanup the PJTestKorpKick
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_korp_accept(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    # We create a PJTestKorpAccept
    PJTEST_BODY['name'] = 'PJTestKorpAccept'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestKorpAccept)
    target = [x for x in pcs if x['name'] == 'PJTestKorpAccept'][0]

    # We invite PJTestKorpAccept
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp invite OK' in response.json().get("msg")

    # PJTestKorpAccept accepts the request
    response = requests.post(f"{API_URL}/mypc/{target['_id']}/korp/{korp_id}/accept", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp accept OK' in response.json().get("msg")

    # We cleanup the PJTestKorpAccept
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_korp_decline(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    # We create a PJTestKorpDecline
    PJTEST_BODY['name'] = 'PJTestKorpDecline'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestKorpAccept)
    target = [x for x in pcs if x['name'] == 'PJTestKorpDecline'][0]

    # We invite PJTestKorpDecline
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp invite OK' in response.json().get("msg")

    # PJTestKorpDecline declines the request
    response = requests.post(f"{API_URL}/mypc/{target['_id']}/korp/{korp_id}/decline", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp decline OK' in response.json().get("msg")

    # We cleanup the PJTestKorpDecline
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_korp_leave(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    # We create a PJTestKorpLeave
    PJTEST_BODY['name'] = 'PJTestKorpLeave'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestKorpAccept)
    target = [x for x in pcs if x['name'] == 'PJTestKorpLeave'][0]

    # We invite PJTestKorpLeave
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp invite OK' in response.json().get("msg")

    # PJTestKorpLeave leave the request
    response = requests.post(f"{API_URL}/mypc/{target['_id']}/korp/{korp_id}/leave", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp leave OK' in response.json().get("msg")

    # We cleanup the PJTestKorpLeave
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_korp_delete(jwt_header, mypc):
    korp_id = mypc['indexed'][CREATURE_ID]['korp']['id']

    response = requests.delete(f"{API_URL}/mypc/{CREATURE_ID}/korp/{korp_id}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Korp delete OK' in response.json().get("msg")
