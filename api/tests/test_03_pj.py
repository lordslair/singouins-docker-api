# -*- coding: utf8 -*-

import json
import requests

pjname_test = 'PJTest'
payload     = {'username': 'user', 'password': 'plop'}
payload_c   = {'race': 'Ruzé', 'name': 'PJTest'}

def test_singouins_pj_create():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url       = 'https://api.proto.singouins.com/mypc'
    response  = requests.post(url, json = payload_c, headers=headers)

    assert response.status_code == 201

def test_singouins_pj_infos():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/pc/name/{}'.format(pjname_test)
    response = requests.get(url, headers=headers)
    name     = json.loads(response.text)['name']

    assert name == pjname_test
    assert response.status_code == 200
