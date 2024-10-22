# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID


def test_singouins_public_pc(jwt_header):
    response  = requests.get(f'{API_URL}/pc/{CREATURE_ID}', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_public_pc_events(jwt_header):
    response  = requests.get(f'{API_URL}/pc/{CREATURE_ID}/event', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True


def test_singouins_public_pc_item(jwt_header):
    response  = requests.get(f'{API_URL}/pc/{CREATURE_ID}/item', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True
