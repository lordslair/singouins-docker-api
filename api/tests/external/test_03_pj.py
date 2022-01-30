# -*- coding: utf8 -*-

import json
import os
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       PJ_NAME)

def test_singouins_pj_create():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}
    payload     = {'name': PJ_NAME,
                   'gender': True,
                   'race': '2',
                   'class': '3',
                   'cosmetic': {'metaid': 8, 'data': {'hasGender': True, 'beforeArmor': False, 'hideArmor': None}},
                   'equipment': {'righthand': {'metaid': 34, 'metatype': 'weapon'}, 'lefthand': {'metaid': 11, 'metatype': 'weapon'}}}

    url      = f'{API_URL}/mypc'
    response = requests.post(url, json = payload, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] == True

def test_singouins_pj_infos():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjname   = json.loads(response.text)['payload'][0]['name']

    assert pjname == PJ_NAME
    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
