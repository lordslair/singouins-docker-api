# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       AUTH_PAYLOAD)

def test_singouins_pj_delete():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}'
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_auth_delete():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/auth/delete'
    response = requests.delete(url, json = {'username': 'user@exemple.com'}, headers=headers)

    assert response.status_code == 200
