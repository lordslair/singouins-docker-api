# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)


def test_singouins_mp_send():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pcid}/mp'  # POST
    response  = requests.post(url,
                              json={"src": pcid,
                                    "dst": [pcid],
                                    "subject":
                                        "MP Subject", "body": "MP Body"
                                    },
                              headers=headers)

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_mp_list():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pcid}/mp'  # GET
    response = requests.get(url, headers=headers)
    subject  = json.loads(response.text)['payload'][0]['subject']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert subject == "MP Subject"


def test_singouins_mp_get():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pcid}/mp'  # GET
    response = requests.get(url, headers=headers)
    mpid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pcid}/mp/{mpid}'  # GET
    response = requests.get(url, headers=headers)
    body     = json.loads(response.text)['payload']['body']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert body == "MP Body"


def test_singouins_mp_delete():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pcid}/mp'  # GET
    response = requests.get(url, headers=headers)
    mpid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pcid}/mp/{mpid}'  # DELETE
    response = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mp_addressbook():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url      = f'{API_URL}/mypc/{pcid}/mp/addressbook'  # GET
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
