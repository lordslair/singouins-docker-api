# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)


def test_singouins_action_unload():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    itemid     = json.loads(response.text)['payload']['weapon'][0]['id']
    metaid     = json.loads(response.text)['payload']['weapon'][0]['metaid']

    assert metaid == 34  # Needs to be a Pistolet

    url       = f'{API_URL}/mypc/{pcid}/action/unload/{itemid}'  # POST
    response  = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Unload Query OK' in json.loads(response.text)['msg']
    assert json.loads(response.text)['payload']['weapon']['ammo'] == 0

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    wallet     = json.loads(response.text)['payload']['wallet']

    assert wallet['ammo']['cal22'] > 0


def test_singouins_action_reload():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    itemid     = json.loads(response.text)['payload']['weapon'][0]['id']
    metaid     = json.loads(response.text)['payload']['weapon'][0]['metaid']

    assert metaid == 34  # Needs to be a Pistolet

    url       = f'{API_URL}/mypc/{pcid}/action/reload/{itemid}'  # POST
    response  = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Reload Query OK' in json.loads(response.text)['msg']
    assert json.loads(response.text)['payload']['weapon']['ammo'] == 6

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    wallet     = json.loads(response.text)['payload']['wallet']

    assert wallet['ammo']['cal22'] == 0
