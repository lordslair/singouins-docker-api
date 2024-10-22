# -*- coding: utf8 -*-

import requests

from variables import API_URL, MAP_ID


def test_singouins_map(jwt_header):
    response  = requests.get(f'{API_URL}/map/{MAP_ID}', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True
