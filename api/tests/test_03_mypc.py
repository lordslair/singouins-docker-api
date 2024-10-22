# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID, CREATURE_NAME, PJTEST_BODY


def test_singouins_mypc_create(jwt_header):
    response  = requests.post(f'{API_URL}/mypc', headers=jwt_header['access'], json=PJTEST_BODY)
    assert response.status_code == 201
    assert response.json().get("success") is True


def test_singouins_mypc_get(mypc):
    assert mypc['indexed'][CREATURE_ID]['name'] == CREATURE_NAME


def test_singouins_mypc_view(jwt_header):
    response  = requests.get(f'{API_URL}/mypc/{CREATURE_ID}/view', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_mypc_actives(jwt_header):
    for actives_type in ['cds', 'effects', 'statuses']:
        response  = requests.get(f'{API_URL}/mypc/{CREATURE_ID}/actives/{actives_type}', headers=jwt_header['access'])  # noqa: E501
        assert response.status_code == 200
        assert response.json().get("success") is True
        assert isinstance(response.json().get("payload")[actives_type], list)
