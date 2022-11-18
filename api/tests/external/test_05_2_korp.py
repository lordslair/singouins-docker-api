# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)

# To reuse in many calls
payload_pjtest = {
    'name': 'PJTestKorpInvite',
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


def test_singouins_korp_create():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pcid}/korp'  # POST
    payload_s = {"name": 'KorpTest'}
    response  = requests.post(url, json=payload_s, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True
    assert 'Korp create OK' in json.loads(response.text)['msg']


def test_singouins_korp_get():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid   = pc['korp']

    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    members = json.loads(response.text)['payload']['members']
    # We need the PC (name:PJTest)
    pc  = [x for x in members if x['name'] == 'PJTest'][0]
    assert pc['korp_rank'] == 'Leader'
    assert 'Korp Query OK' in json.loads(response.text)['msg']


def test_singouins_korp_invite():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid   = pc['korp']

    # We create a PJTestKorpInvite
    payload_pjtest['name'] = 'PJTestKorpInvite'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTestKorpInvite)
    target   = [x for x in pcs if x['name'] == 'PJTestKorpInvite'][0]
    targetid = target['id']

    # We invite PJTestKorpInvite
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpInvite
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_kick():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid  = pc['korp']

    # We create a PJTestKorpKick
    payload_pjtest['name'] = 'PJTestKorpInvite'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTestKorpInvite)
    target   = [x for x in pcs if x['name'] == 'PJTestKorpInvite'][0]
    targetid = target['id']

    # We invite PJTestKorpKick
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # We kick PJTestKorpKick
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/kick/{targetid}'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp kick OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpKick
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_accept():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid  = pc['korp']

    # We create a PJTestKorpAccept
    payload_pjtest['name'] = 'PJTestKorpAccept'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTestKorpAccept)
    target   = [x for x in pcs if x['name'] == 'PJTestKorpAccept'][0]
    targetid = target['id']

    # We invite PJTestKorpAccept
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}'  # POST# noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # PJTestKorpAccept accepts the request
    url      = f'{API_URL}/mypc/{targetid}/korp/{korpid}/accept'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp accept OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpAccept
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_decline():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid  = pc['korp']

    # We create a PJTestKorpDecline
    payload_pjtest['name'] = 'PJTestKorpDecline'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTestKorpAccept)
    target   = [x for x in pcs if x['name'] == 'PJTestKorpDecline'][0]
    targetid = target['id']

    # We invite PJTestKorpDecline
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # PJTestKorpDecline declines the request
    url      = f'{API_URL}/mypc/{targetid}/korp/{korpid}/decline'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp decline OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpDecline
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_leave():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid  = pc['korp']

    # We create a PJTestKorpLeave
    payload_pjtest['name'] = 'PJTestKorpLeave'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTestKorpAccept)
    target   = [x for x in pcs if x['name'] == 'PJTestKorpLeave'][0]
    targetid = target['id']

    # We invite PJTestKorpLeave
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp invite OK' in json.loads(response.text)['msg']

    # PJTestKorpLeave leave the request
    url      = f'{API_URL}/mypc/{targetid}/korp/{korpid}/leave'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp leave OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestKorpLeave
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_korp_delete():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == 'PJTest'][0]
    pcid     = pc['id']
    korpid  = pc['korp']

    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korp delete OK' in json.loads(response.text)['msg']
