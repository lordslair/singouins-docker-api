# -*- coding: utf8 -*-

import json
import os
import requests

API_URL     = os.environ['SEP_API_URL']
pjname_test = 'PJTest'
payload     = {'username': 'user@exemple.com', 'password': 'plop'}

def test_singouins_pa():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')

    url      = API_URL + '/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url       = API_URL + '/mypc/{}/pa'.format(pjid)
    response  = requests.get(url, headers=headers)
    bluettnpa = json.loads(response.text)['payload']['blue']['ttnpa']
    redttnpa  = json.loads(response.text)['payload']['red']['ttnpa']

    assert json.loads(response.text)['success'] == True
    assert bluettnpa > 0
    assert redttnpa > 0
    assert response.status_code == 200
