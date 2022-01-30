# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)

def test_singouins_pa():
    url      = f'{API_URL}/auth/login'
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'
    response = requests.get(url, headers=headers)
    pjid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pjid}/pa'
    response  = requests.get(url, headers=headers)
    bluettnpa = json.loads(response.text)['payload']['blue']['ttnpa']
    redttnpa  = json.loads(response.text)['payload']['red']['ttnpa']

    assert json.loads(response.text)['success'] == True
    assert bluettnpa > 0
    assert redttnpa > 0
    assert response.status_code == 200
