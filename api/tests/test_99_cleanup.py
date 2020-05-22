# -*- coding: utf8 -*-

import json
import requests

pjname_test = 'PJTest'
payload  = {'username': 'user', 'password': 'plop'}

def test_singouins_pj_delete():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/pj/infos/name/{}'.format(pjname_test)
    response = requests.get(url)
    pjid     = json.loads(response.text)['id']
    url      = 'https://api.proto.singouins.com/pj/delete/id/{}'.format(pjid)
    response = requests.delete(url, headers=headers)
    print(response.text)

    assert response.status_code == 200

def test_singouins_auth_delete():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/auth/delete/user'
    response = requests.delete(url, json = {'username': 'user'}, headers=headers)
    print(response.text)

    assert response.status_code == 200
