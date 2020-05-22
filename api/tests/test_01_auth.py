# -*- coding: utf8 -*-

import json
import requests

payload     = {'username': 'user', 'password': 'plop'}

def test_singouins_auth_register():
    url       = 'https://api.proto.singouins.com/auth/register'
    payload_c = {'username': 'user', 'password': 'plop', 'mail': 'user@exemple.com'}
    response  = requests.post(url, json = payload_c)
    print(response.text)

    assert response.status_code == 201

def test_singouins_auth_login():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    print(response.text)

    assert response.status_code == 200
    assert json.loads(response.text)

def test_singouins_auth_infos():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/auth/infos'
    response = requests.get(url, headers=headers)
    infos    = json.loads(response.text)
    print(response.text)

    assert response.status_code == 200
    assert infos['logged_in_as'] == 'user'

def test_singouins_auth_refresh():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['refresh_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url       = 'https://api.proto.singouins.com/auth/refresh'
    response = requests.post(url, headers=headers)
    refreshed = json.loads(response.text)
    print(response.text)

    assert response.status_code == 200
    assert refreshed['access_token']
