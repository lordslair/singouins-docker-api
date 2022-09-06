# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)


def test_singouins_pa():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url       = f'{API_URL}/mypc/{pcid}/pa'  # GET
    response  = requests.get(url, headers=headers)
    bluettnpa = json.loads(response.text)['payload']['blue']['ttnpa']
    redttnpa  = json.loads(response.text)['payload']['red']['ttnpa']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert bluettnpa > 0
    assert redttnpa > 0
