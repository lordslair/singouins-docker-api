# -*- coding: utf8 -*-

import json
import os
import requests

SEP_URL     = os.environ['SEP_URL']
pjname_test = 'PJTest'
payload     = {'username': 'user', 'password': 'plop'}

def test_singouins_squad_create():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url       = SEP_URL + '/mypc/{}/squad'.format(pjid)
    payload_s = {"name": 'SquadTest'}
    response  = requests.post(url, json = payload_s, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 201

def test_singouins_squad_get():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    url      = SEP_URL + '/mypc/{}/squad/{}'.format(pjid,squadid)
    response = requests.get(url, headers=headers)
    squad_r  = json.loads(response.text)['payload']['members'][0]['squad_rank']

    assert squad_r == 'Leader'
    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_squad_invite_and_kick():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    url      = SEP_URL + '/mypc/{}/squad/{}/invite/1'.format(pjid,squadid)
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == False
    assert 'already in a squad' in json.loads(response.text)['msg']
    assert response.status_code == 200

    # We create a PJTestSquad just to invite/kick
    url      = SEP_URL + '/mypc'
    response = requests.post(url, json = {'race': '3', 'name': 'PJTestSquad'}, headers=headers)
    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    targetid = json.loads(response.text)['payload'][1]['id']

    url      = SEP_URL + '/mypc/{}/squad/{}/invite/{}'.format(pjid,squadid,targetid)
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert 'PC successfully invited' in json.loads(response.text)['msg']
    assert response.status_code == 201

    url      = SEP_URL + '/mypc/{}/squad/{}/kick/{}'.format(pjid,squadid,targetid)
    response = requests.post(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert 'PC successfully kicked' in json.loads(response.text)['msg']
    assert response.status_code == 200

    # We cleanup the PJTestSquad
    url      = SEP_URL + '/mypc/{}'.format(targetid)
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_squad_delete():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']
    squadid  = json.loads(response.text)['payload'][0]['squad']

    url      = SEP_URL + '/mypc/{}/squad/{}'.format(pjid,squadid)
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
