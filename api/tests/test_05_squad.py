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

    assert response.status_code == 200
