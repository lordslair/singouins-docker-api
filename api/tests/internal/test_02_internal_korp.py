# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS,
                       KORP_ID)

def test_singouins_internal_korp():
    url       = f'{API_URL}/internal/korp'
    payload   = {"korpid": KORP_ID}
    response  = requests.post(url, headers=HEADERS, json = payload)

    assert response.status_code == 200

def test_singouins_internal_korps():
    url       = f'{API_URL}/internal/korps'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
