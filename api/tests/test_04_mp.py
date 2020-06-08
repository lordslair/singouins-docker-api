# -*- coding: utf8 -*-

import json
import requests

pjname_test = 'PJTest'
payload     = {'username': 'user', 'password': 'plop'}

def test_singouins_mp_send():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/pc/name/{}'.format(pjname_test)
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['id']

    url       = 'https://api.proto.singouins.com/mypc/{}/mp'.format(pjid)
    payload_s = {"src": pjid, "dst": [pjid], "subject": "MP Subject", "body": "MP Body"}
    response  = requests.post(url, json = payload_s, headers=headers)

    assert response.status_code == 201

def test_singouins_mp_list():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/pc/name/{}'.format(pjname_test)
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['id']

    url       = 'https://api.proto.singouins.com/mypc/{}/mp'.format(pjid)
    response  = requests.get(url, headers=headers)
    subject   = json.loads(response.text)[0]['subject']

    assert subject == "MP Subject"
    assert response.status_code == 200

def test_singouins_mp_get():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/pc/name/{}'.format(pjname_test)
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['id']

    url       = 'https://api.proto.singouins.com/mypc/{}/mp'.format(pjid)
    response  = requests.get(url, headers=headers)
    mpid      = json.loads(response.text)[0]['id']

    url       = 'https://api.proto.singouins.com/mypc/{}/mp/{}'.format(pjid,mpid)
    response  = requests.get(url, headers=headers)
    body      = json.loads(response.text)['body']

    assert body == "MP Body"
    assert response.status_code == 200

def test_singouins_mp_delete():
    url      = 'https://api.proto.singouins.com/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = 'https://api.proto.singouins.com/pc/name/{}'.format(pjname_test)
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['id']

    url       = 'https://api.proto.singouins.com/mypc/{}/mp'.format(pjid)
    response  = requests.get(url, headers=headers)
    mpid      = json.loads(response.text)[0]['id']

    url       = 'https://api.proto.singouins.com/mypc/{}/mp/{}'.format(pjid,mpid)
    response  = requests.delete(url, headers=headers)

    assert response.status_code == 200
