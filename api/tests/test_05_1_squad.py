# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID, PJTEST_BODY


def test_singouins_squad_create(jwt_header):
    response = requests.post(f'{API_URL}/mypc/{CREATURE_ID}/squad', headers=jwt_header['access'], json={"name": 'SquadTest'})  # noqa: E501

    assert response.status_code == 201
    assert response.json().get("success") is True
    assert 'Squad create OK' in response.json().get("msg")


def test_singouins_squad_get(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    response = requests.get(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}", headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    members = response.json().get("payload")['members']
    # We need the PC (name:PJTest)
    pc  = [x for x in members if x['name'] == 'PJTest'][0]
    assert pc['squad']['rank'] == 'Leader'
    assert 'Squad Query OK' in response.json().get("msg")


def test_singouins_squad_invite(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    # We create a PJTestSquadInvite
    PJTEST_BODY['name'] = 'PJTestSquadInvite'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestSquadInvite)
    target = [x for x in pcs if x['name'] == 'PJTestSquadInvite'][0]

    # We invite PJTestSquadInvite
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad invite OK' in response.json().get("msg")

    # We cleanup the PJTestSquadInvite
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_squad_kick(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    # We create a PJTestSquadKick
    PJTEST_BODY['name'] = 'PJTestSquadInvite'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestSquadInvite)
    target = [x for x in pcs if x['name'] == 'PJTestSquadInvite'][0]

    # We invite PJTestSquadKick
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad invite OK' in response.json().get("msg")

    # We kick PJTestSquadKick
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}/kick/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad kick OK' in response.json().get("msg")

    # We cleanup the PJTestSquadKick
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_squad_accept(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    # We create a PJTestSquadAccept
    PJTEST_BODY['name'] = 'PJTestSquadAccept'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestSquadAccept)
    target = [x for x in pcs if x['name'] == 'PJTestSquadAccept'][0]

    # We invite PJTestSquadAccept
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad invite OK' in response.json().get("msg")

    # PJTestSquadAccept accepts the request
    response = requests.post(f"{API_URL}/mypc/{target['_id']}/squad/{squad_id}/accept", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad accept OK' in response.json().get("msg")

    # We cleanup the PJTestSquadAccept
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_squad_decline(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    # We create a PJTestSquadDecline
    PJTEST_BODY['name'] = 'PJTestSquadDecline'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestSquadAccept)
    target = [x for x in pcs if x['name'] == 'PJTestSquadDecline'][0]

    # We invite PJTestSquadDecline
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad invite OK' in response.json().get("msg")

    # PJTestSquadDecline declines the request
    response = requests.post(f"{API_URL}/mypc/{target['_id']}/squad/{squad_id}/decline", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad decline OK' in response.json().get("msg")

    # We cleanup the PJTestSquadDecline
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_squad_leave(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    # We create a PJTestSquadLeave
    PJTEST_BODY['name'] = 'PJTestSquadLeave'
    response = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    response = requests.get(f'{API_URL}/mypc', headers=jwt_header['access'])

    pcs = response.json().get("payload")
    # We need the PC (name:PJTestSquadAccept)
    target = [x for x in pcs if x['name'] == 'PJTestSquadLeave'][0]

    # We invite PJTestSquadLeave
    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}/invite/{target['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad invite OK' in response.json().get("msg")

    # PJTestSquadLeave leave the request
    response = requests.post(f"{API_URL}/mypc/{target['_id']}/squad/{squad_id}/leave", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad leave OK' in response.json().get("msg")

    # We cleanup the PJTestSquadLeave
    response = requests.delete(f"{API_URL}/mypc/{target['_id']}", headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_squad_delete(jwt_header, mypc):
    squad_id = mypc['indexed'][CREATURE_ID]['squad']['id']

    response = requests.delete(f"{API_URL}/mypc/{CREATURE_ID}/squad/{squad_id}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert 'Squad delete OK' in response.json().get("msg")
