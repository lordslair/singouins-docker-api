# -*- coding: utf8 -*-

import json
import requests

from variables import (API_INTERNAL_TOKEN,
                       API_URL)

def test_singouins_internal_meta():
    url       = f'{API_URL}/internal/meta/weapons'
    headers   = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/armors'
    headers   = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/skills'
    headers   = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/effects'
    headers   = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True

    url       = f'{API_URL}/internal/meta/races'
    headers   = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
