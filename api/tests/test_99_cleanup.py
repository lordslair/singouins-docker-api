# -*- coding: utf8 -*-

import json
import os
import requests

SEP_URL     = os.environ['SEP_URL']
pjname_test = 'PJTest'
payload  = {'username': 'user', 'password': 'plop'}

def test_singouins_pj_delete():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = SEP_URL + '/mypc/{}'.format(pjid)
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_auth_delete():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = SEP_URL + '/auth/delete/user'
    response = requests.delete(url, json = {'username': 'user'}, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
