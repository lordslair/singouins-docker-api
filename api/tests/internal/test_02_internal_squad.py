# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS,
                       SQUAD_ID)


def test_singouins_internal_squad():
    squadid   = SQUAD_ID
    url       = f'{API_URL}/internal/squad/{squadid}'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is False
    assert 'Squad Query KO' in json.loads(response.text)['msg']


def test_singouins_internal_squads():
    url       = f'{API_URL}/internal/squads'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Squads Query OK' in json.loads(response.text)['msg']
