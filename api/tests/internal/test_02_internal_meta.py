# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS)

def test_singouins_internal_meta():
    url       = f'{API_URL}/internal/meta/weapons'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/armors'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/skills'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/effects'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/races'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
