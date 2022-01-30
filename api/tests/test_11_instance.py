# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       AUTH_PAYLOAD)

def test_singouins_mypc_instance_get():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)

    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}'
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_mypc_instance_leave():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)

    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}/leave'
    response = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

def test_singouins_mypc_instance_create():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)

    pcid       = json.loads(response.text)['payload'][0]['id']
    instanceid = json.loads(response.text)['payload'][0]['instance']

    url      = f'{API_URL}/mypc/{pcid}/instance'
    payload  = {"mapid": 1,
                "hardcore": True,
                "fast": False,
                "public": True}
    response = requests.put(url, json = payload, headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] == True
