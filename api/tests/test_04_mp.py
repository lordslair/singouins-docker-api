# -*- coding: utf8 -*-

import json
import os
import requests

API_URL     = os.environ['SEP_API_URL']
pjname_test = 'PJTest'
payload     = {'username': 'user@exemple.com', 'password': 'plop'}

def test_singouins_mp_send():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url       = API_URL + '/mypc/{}/mp'.format(pjid)
    payload_s = {"src": pjid, "dst": [pjid], "subject": "MP Subject", "body": "MP Body"}
    response  = requests.post(url, json = payload_s, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 201

def test_singouins_mp_list():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}/mp'.format(pjid)
    response = requests.get(url, headers=headers)
    subject  = json.loads(response.text)['payload'][0]['subject']

    assert json.loads(response.text)['success'] == True
    assert subject == "MP Subject"
    assert response.status_code == 200

def test_singouins_mp_get():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}/mp'.format(pjid)
    response = requests.get(url, headers=headers)
    mpid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}/mp/{}'.format(pjid,mpid)
    response = requests.get(url, headers=headers)
    body     = json.loads(response.text)['payload']['body']

    assert json.loads(response.text)['success'] == True
    assert body == "MP Body"
    assert response.status_code == 200

def test_singouins_mp_delete():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}/mp'.format(pjid)
    response = requests.get(url, headers=headers)
    mpid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}/mp/{}'.format(pjid,mpid)
    response = requests.delete(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200

def test_singouins_mp_addressbook():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url      = API_URL + '/mypc/{}/mp/addressbook'.format(pjid)
    response = requests.get(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
