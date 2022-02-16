# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       CREATURE_ID)

def test_singouins_korp_create():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pcid}/korp' # POST
    payload_k = {"name": 'KorpTest'}
    response  = requests.post(url, json = payload_k, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 201

def test_singouins_korp_get():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}' # GET
    response = requests.get(url, headers=headers)
    korp_r   = json.loads(response.text)['payload']['members'][0]['korp_rank']

    assert korp_r == 'Leader'
    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_korp_invite():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    # We create a PJTestKorpKick
    url      = f'{API_URL}/mypc' # POST
    payload_c   = {'name': 'PJTestKorpInvite',
                   'gender': True,
                   'race': 2,
                   'class': 3,
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}
    response = requests.post(url, json = payload_c, headers=headers)
    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestKorpInvite
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # We cleanup the PJTestKorpKick
    url      = f'{API_URL}/mypc/{targetid}' # DELETE
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_korp_kick():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    # We create a PJTestKorpKick
    url      = f'{API_URL}/mypc' # POST
    payload_c   = {'name': 'PJTestKorpKick',
                   'gender': True,
                   'race': 2,
                   'class': 3,
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}
    response = requests.post(url, json = payload_c, headers=headers)
    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestKorpKick
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # We kick PJTestKorpKick
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/kick/{targetid}' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # We cleanup the PJTestKorpKick
    url      = f'{API_URL}/mypc/{targetid}' # DELETE
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_korp_accept():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    # We create a PJTestKorpAccept
    url      = f'{API_URL}/mypc' # POST
    payload_c   = {'name': 'PJTestKorpAccept',
                   'gender': True,
                   'race': 2,
                   'class': 3,
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}
    response = requests.post(url, json = payload_c, headers=headers)
    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestKorpAccept
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # PJTestKorpAccept accepts the request
    url      = f'{API_URL}/mypc/{targetid}/korp/{korpid}/accept' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # We cleanup the PJTestKorpAccept
    url      = f'{API_URL}/mypc/{targetid}' # DELETE
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_korp_decline():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    # We create a PJTestKorpDecline
    url      = f'{API_URL}/mypc' # POST
    payload_c   = {'name': 'PJTestKorpDecline',
                   'gender': True,
                   'race': 2,
                   'class': 3,
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}
    response = requests.post(url, json = payload_c, headers=headers)
    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestKorpDecline
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # PJTestKorpDecline declines the request
    url      = f'{API_URL}/mypc/{targetid}/korp/{korpid}/decline' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # We cleanup the PJTestKorpDecline
    url      = f'{API_URL}/mypc/{targetid}' # DELETE
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_korp_leave():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    # We create a PJTestKorpLeave
    url      = f'{API_URL}/mypc' # POST
    payload_c   = {'name': 'PJTestKorpLeave',
                   'gender': True,
                   'race': 2,
                   'class': 3,
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}
    response = requests.post(url, json = payload_c, headers=headers)
    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    # We invite PJTestKorpLeave
    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}/invite/{targetid}' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # PJTestKorpLeave leave the request
    url      = f'{API_URL}/mypc/{targetid}/korp/{korpid}/leave' # POST
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

    # We cleanup the PJTestKorpLeave
    url      = f'{API_URL}/mypc/{targetid}' # DELETE
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_korp_delete():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    korpid   = json.loads(response.text)['payload'][0]['korp']

    url      = f'{API_URL}/mypc/{pcid}/korp/{korpid}' # DELETE
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
