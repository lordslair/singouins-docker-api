# -*- coding: utf8 -*-

import json
import os
import requests

API_URL     = os.environ['SEP_API_URL']
pjname_test = 'PJTest'
payload     = {'username': 'user@exemple.com', 'password': 'plop'}

def test_singouins_pj_delete():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}'.format(pjid)
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_auth_delete():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/auth/delete'
    response = requests.delete(url, json = {'username': 'user@exemple.com'}, headers=headers)

    assert response.status_code == 200
