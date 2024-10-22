# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID


def test_singouins_item(jwt_header):
    response  = requests.get(f'{API_URL}/mypc/{CREATURE_ID}/item', headers=jwt_header['access'])

    assert response.status_code == 200
    assert response.json().get("success") is True
