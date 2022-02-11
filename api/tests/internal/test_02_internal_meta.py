# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS)

def test_singouins_internal_meta():
    url       = f'{API_URL}/internal/meta/weapon'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/armor'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/skill'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/effect'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/race'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
