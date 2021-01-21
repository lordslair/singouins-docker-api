# -*- coding: utf8 -*-

import json
import os
import requests

SEP_URL     = os.environ['SEP_URL']
pjname_test = 'PJTest'
payload     = {'username': 'user@exemple.com', 'password': 'plop'}
payload_c   = {'race': '2', 'name': 'PJTest'}

def test_singouins_pj_create():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.post(url, json = payload_c, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] == True

def test_singouins_pj_infos():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjname   = json.loads(response.text)['payload'][0]['name']

    assert pjname == pjname_test
    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
