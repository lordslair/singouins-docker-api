# -*- coding: utf8 -*-

import json
import os
import requests

API_URL     = os.environ['SEP_API_URL']
mapid       = 1
payload     = {'username': 'user@exemple.com', 'password': 'plop'}

def test_singouins_map():
    url      = API_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')


    url      = API_URL + '/map/{}'.format(mapid)
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
