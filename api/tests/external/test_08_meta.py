# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       METAS)

def test_singouins_meta():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    for meta in METAS:
        url      = f'{API_URL}/meta/item/{meta}' # GET
        response = requests.get(url, headers=headers)

        assert response.status_code == 200
        assert json.loads(response.text)['success'] == True
