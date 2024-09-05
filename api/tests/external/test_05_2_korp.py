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
    'name': 'PJTestKorpInvite',
    'gender': True,
    'race': 2,
    'vocation': 3,
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
KORP_BODY = {"name": 'KorpTest'}


def test_singouins_korp_create():
    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/korp',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json=KORP_BODY,
        )

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True
    assert 'Korp create OK' in json.loads(response.text)['msg']


def test_singouins_korp_get():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]

    response = requests.get(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{pc['korp']['id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    members = json.loads(response.text)['payload']['members']
    # We need the PC (name:PJTest)
    pc  = [x for x in members if x['name'] == 'PJTest'][0]
    assert pc['korp']['rank'] == 'Leader'
    assert 'Korp Query OK' in json.loads(response.text)['msg']


def test_singouins_korp_invite():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    korpid  = pc['korp']['id']

    # We create a PJTestKorpInvite
    PJTEST_BODY['name'] = 'PJTestKorpInvite'

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
    # We need the PC (name:PJTestKorpInvite)
    target = [x for x in pcs if x['name'] == 'PJTestKorpInvite'][0]
    # We invite PJTestKorpInvite
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{korpid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpInvite
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_kick():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    korpid  = pc['korp']['id']

    # We create a PJTestKorpKick
    PJTEST_BODY['name'] = 'PJTestKorpInvite'

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
    # We need the PC (name:PJTestKorpInvite)
    target = [x for x in pcs if x['name'] == 'PJTestKorpInvite'][0]

    # We invite PJTestKorpKick
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{korpid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # We kick PJTestKorpKick
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{korpid}/kick/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp kick OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpKick
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_accept():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    korpid  = pc['korp']['id']

    # We create a PJTestKorpAccept
    PJTEST_BODY['name'] = 'PJTestKorpAccept'
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
    # We need the PC (name:PJTestKorpAccept)
    target = [x for x in pcs if x['name'] == 'PJTestKorpAccept'][0]

    # We invite PJTestKorpAccept
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{korpid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # PJTestKorpAccept accepts the request
    response = requests.post(
        f"{API_URL}/mypc/{target['_id']}/korp/{korpid}/accept",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp accept OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpAccept
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_decline():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    korpid  = pc['korp']['id']

    # We create a PJTestKorpDecline
    PJTEST_BODY['name'] = 'PJTestKorpDecline'

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
    # We need the PC (name:PJTestKorpAccept)
    target = [x for x in pcs if x['name'] == 'PJTestKorpDecline'][0]

    # We invite PJTestKorpDecline
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{korpid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # PJTestKorpDecline declines the request
    response = requests.post(
        f"{API_URL}/mypc/{target['_id']}/korp/{korpid}/decline",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp decline OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpDecline
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_leave():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == 'PJTest'][0]
    korpid  = pc['korp']['id']

    # We create a PJTestKorpLeave
    PJTEST_BODY['name'] = 'PJTestKorpLeave'

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
    # We need the PC (name:PJTestKorpAccept)
    target = [x for x in pcs if x['name'] == 'PJTestKorpLeave'][0]

    # We invite PJTestKorpLeave
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{korpid}/invite/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # PJTestKorpLeave leave the request
    response = requests.post(
        f"{API_URL}/mypc/{target['_id']}/korp/{korpid}/leave",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp leave OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpLeave
    response = requests.delete(
        f"{API_URL}/mypc/{target['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_delete():
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
        f"{API_URL}/mypc/{CREATURE_ID}/korp/{pc['korp']['id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp delete OK' in json.loads(response.text)['msg']
