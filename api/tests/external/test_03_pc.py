# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       PC_NAME)

def test_singouins_pc_create():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}
    payload     = {'name': PC_NAME,
                   'gender': True,
                   'race': 2,
                   'class': 3,
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}

    url      = f'{API_URL}/mypc' # POST
    response = requests.post(url, json = payload, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] == True

def test_singouins_pc_infos():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcname   = json.loads(response.text)['payload'][0]['name']

    assert pcname == PC_NAME
    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_pc_view():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url      = f'{API_URL}/mypc/{pcid}/view' # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_pc_stats():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url      = f'{API_URL}/mypc/{pcid}/stats' # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_pc_effects():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url      = f'{API_URL}/mypc/{pcid}/effects' # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_pc_cds():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url      = f'{API_URL}/mypc/{pcid}/cds' # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_pc_skills():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url      = f'{API_URL}/mypc/{pcid}/skills' # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
