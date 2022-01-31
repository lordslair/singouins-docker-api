# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)

def test_singouins_auth_register():
    url       = f'{API_URL}/auth/register'
    payload   = {'password': 'plop', 'mail': 'user@exemple.com'}
    response  = requests.post(url, json = payload)

    assert response.status_code == 201

def test_singouins_auth_login():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)

    assert response.status_code == 200
    assert json.loads(response.text)

def test_singouins_auth_infos():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/auth/infos'
    response = requests.get(url, headers=headers)
    infos    = json.loads(response.text)

    assert response.status_code == 200
    assert infos['logged_in_as'] == 'user@exemple.com'

def test_singouins_auth_refresh():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['refresh_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url       = f'{API_URL}/auth/refresh'
    response  = requests.post(url, headers=headers)
    refreshed = json.loads(response.text)

    assert response.status_code == 200
    assert refreshed['access_token']