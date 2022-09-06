# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)

# To reuse in many calls
payload_pjtest = {
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


def test_singouins_squad_create():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pcid}/squad'  # POST
    payload_s = {"name": 'SquadTest'}
    response  = requests.post(url, json=payload_s, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True
    assert 'Squad create OK' in json.loads(response.text)['msg']


def test_singouins_squad_get():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    squad_r  = json.loads(response.text)['payload']['members'][0]['squad_rank']
    assert squad_r == 'Leader'
    assert 'Squad Query OK' in json.loads(response.text)['msg']


def test_singouins_squad_invite():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    # We create a PJTestSquadInvite
    payload_pjtest['name'] = 'PJTestSquadInvite'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestSquadInvite
    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadInvite
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_kick():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    # We create a PJTestSquadKick
    payload_pjtest['name'] = 'PJTestSquadInvite'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestSquadKick
    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # We kick PJTestSquadKick
    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}/kick/{targetid}'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad kick OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadKick
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_accept():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    # We create a PJTestSquadAccept
    payload_pjtest['name'] = 'PJTestSquadAccept'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestSquadAccept
    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}/invite/{targetid}'  # POST# noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # PJTestSquadAccept accepts the request
    url      = f'{API_URL}/mypc/{targetid}/squad/{squadid}/accept'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad accept OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadAccept
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_decline():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    # We create a PJTestSquadDecline
    payload_pjtest['name'] = 'PJTestSquadDecline'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestSquadDecline
    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # PJTestSquadDecline declines the request
    url      = f'{API_URL}/mypc/{targetid}/squad/{squadid}/decline'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad decline OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadDecline
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_leave():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    # We create a PJTestSquadLeave
    payload_pjtest['name'] = 'PJTestSquadLeave'

    url      = f'{API_URL}/mypc'  # POST
    response = requests.post(url, json=payload_pjtest, headers=headers)
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestSquadLeave
    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}/invite/{targetid}'  # POST # noqa
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad invite OK' in json.loads(response.text)['msg']

    # PJTestSquadLeave leave the request
    url      = f'{API_URL}/mypc/{targetid}/squad/{squadid}/leave'  # POST
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad leave OK' in json.loads(response.text)['msg']

    # We cleanup the PJTestSquadLeave
    url      = f'{API_URL}/mypc/{targetid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_squad_delete():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    url      = f'{API_URL}/mypc/{pcid}/squad/{squadid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squad delete OK' in json.loads(response.text)['msg']
