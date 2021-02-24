# -*- coding: utf8 -*-

import json
import os
import requests

API_URL     = os.environ['SEP_API_URL']
payload     = {'username': 'user@exemple.com', 'password': 'plop'}

def test_singouins_auth_register():
    url       = API_URL + '/auth/register'
    payload_c = {'password': 'plop', 'mail': 'user@exemple.com'}
    response  = requests.post(url, json = payload_c)

    assert response.status_code == 201

def test_singouins_auth_login():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)

    assert response.status_code == 200
    assert json.loads(response.text)

def test_singouins_auth_infos():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/auth/infos'
    response = requests.get(url, headers=headers)
    infos    = json.loads(response.text)

    assert response.status_code == 200
    assert infos['logged_in_as'] == 'user@exemple.com'

def test_singouins_auth_refresh():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['refresh_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url       = API_URL + '/auth/refresh'
    response  = requests.post(url, headers=headers)
    refreshed = json.loads(response.text)

    assert response.status_code == 200
    assert refreshed['access_token']
