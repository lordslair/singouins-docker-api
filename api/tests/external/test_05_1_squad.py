# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    access_token_get,
    )

# To reuse in many calls
PJTEST_BODY = {
    'name': 'PJTestSquadInvite',
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
SQUAD_BODY = {"name": 'SquadTest'}


def test_singouins_squad_create():
    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/squad',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json=SQUAD_BODY,
        )

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True
    assert 'Squad create OK' in json.loads(response.text)['msg']


def test_singouins_squad_get():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]

    response = requests.get(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{pc['squad']['id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    members = json.loads(response.text)['payload']['members']
    # We need the PC (name:PJTest)
    pc  = [x for x in members if x['name'] == 'PJTest'][0]
    assert pc['squad']['rank'] == 'Leader'
    assert 'Squad Query OK' in json.loads(response.text)['msg']


def test_singouins_squad_invite():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    squadid  = pc['squad']['id']

    # We create a PJTestSquadInvite
    PJTEST_BODY['name'] = 'PJTestSquadInvite'

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
    # We need the PC (name:PJTestSquadInvite)
    target = [x for x in pcs if x['name'] == 'PJTestSquadInvite'][0]
    # We invite PJTestSquadInvite
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{squadid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadInvite
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_kick():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    squadid  = pc['squad']['id']

    # We create a PJTestSquadKick
    PJTEST_BODY['name'] = 'PJTestSquadInvite'

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
    # We need the PC (name:PJTestSquadInvite)
    target = [x for x in pcs if x['name'] == 'PJTestSquadInvite'][0]

    # We invite PJTestSquadKick
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{squadid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # We kick PJTestSquadKick
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{squadid}/kick/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad kick OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadKick
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_accept():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    squadid  = pc['squad']['id']

    # We create a PJTestSquadAccept
    PJTEST_BODY['name'] = 'PJTestSquadAccept'
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
    # We need the PC (name:PJTestSquadAccept)
    target = [x for x in pcs if x['name'] == 'PJTestSquadAccept'][0]

    # We invite PJTestSquadAccept
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{squadid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # PJTestSquadAccept accepts the request
    response = requests.post(
        f"{API_URL}/mypc/{target['_id']}/squad/{squadid}/accept",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad accept OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadAccept
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_decline():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    squadid  = pc['squad']['id']

    # We create a PJTestSquadDecline
    PJTEST_BODY['name'] = 'PJTestSquadDecline'

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
    # We need the PC (name:PJTestSquadAccept)
    target = [x for x in pcs if x['name'] == 'PJTestSquadDecline'][0]

    # We invite PJTestSquadDecline
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{squadid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # PJTestSquadDecline declines the request
    response = requests.post(
        f"{API_URL}/mypc/{target['_id']}/squad/{squadid}/decline",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad decline OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadDecline
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_leave():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    squadid  = pc['squad']['id']

    # We create a PJTestSquadLeave
    PJTEST_BODY['name'] = 'PJTestSquadLeave'

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
    # We need the PC (name:PJTestSquadAccept)
    target = [x for x in pcs if x['name'] == 'PJTestSquadLeave'][0]

    # We invite PJTestSquadLeave
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{squadid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # PJTestSquadLeave leave the request
    response = requests.post(
        f"{API_URL}/mypc/{target['_id']}/squad/{squadid}/leave",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad leave OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadLeave
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_delete():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]

    response = requests.delete(
        f"{API_URL}/mypc/{CREATURE_ID}/squad/{pc['squad']['id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad delete OK' in json.loads(response.text)['msg']
