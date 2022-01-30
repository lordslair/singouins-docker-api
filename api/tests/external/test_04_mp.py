# -*- coding: utf8 -*-

import json
import os
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)

def test_singouins_mp_send():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pjid}/mp'
    payload_s = {"src": pjid, "dst": [pjid], "subject": "MP Subject", "body": "MP Body"}
    response  = requests.post(url, json = payload_s, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 201

def test_singouins_mp_list():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}/mp'
    response = requests.get(url, headers=headers)
    subject  = json.loads(response.text)['payload'][0]['subject']

    assert json.loads(response.text)['success'] == True
    assert subject == "MP Subject"
    assert response.status_code == 200

def test_singouins_mp_get():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}/mp'
    response = requests.get(url, headers=headers)
    mpid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}/mp/{mpid}'
    response = requests.get(url, headers=headers)
    body     = json.loads(response.text)['payload']['body']

    assert json.loads(response.text)['success'] == True
    assert body == "MP Body"
    assert response.status_code == 200

def test_singouins_mp_delete():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}/mp'
    response = requests.get(url, headers=headers)
    mpid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}/mp/{mpid}'
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_mp_addressbook():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pjid}/mp/addressbook'
    response = requests.get(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
