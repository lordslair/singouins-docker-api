# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS,
                       KORP_ID)


def test_singouins_internal_korp():
    korpid    = KORP_ID
    url       = f'{API_URL}/internal/korp/{korpid}'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is False
    assert 'Korp Query KO' in json.loads(response.text)['msg']


def test_singouins_internal_korps():
    url       = f'{API_URL}/internal/korps'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Korps Query OK' in json.loads(response.text)['msg']
