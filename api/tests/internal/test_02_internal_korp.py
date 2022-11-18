# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS)


def test_singouins_internal_korp():
    url = f'{API_URL}/internal/korp/11111111-babe-babe-babe-111111111111'
    response = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is False
    assert 'Korp Query KO' in json.loads(response.text)['msg']


def test_singouins_internal_korps():
    url = f'{API_URL}/internal/korps'
    response = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korps Query OK' in json.loads(response.text)['msg']
