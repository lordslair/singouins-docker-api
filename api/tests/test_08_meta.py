# -*- coding: utf8 -*-

import json
import os
import requests

SEP_URL     = os.environ['SEP_URL']
metalist    = ['armor','weapon']
payload     = {'username': 'user', 'password': 'plop'}

def test_singouins_meta():
    url      = SEP_URL + '/auth/login'
    response = requests.post(url, json = payload)
    token    = json.loads(response.text)['access_token']
    headers  = json.loads('{"Authorization": "Bearer '+ token + '"}')


    for meta in metalist:
        url      = SEP_URL + '/meta/item/{}'.format(meta)
        response = requests.get(url, headers=headers)

        assert response.status_code == 200
        assert json.loads(response.text)['success'] == True
