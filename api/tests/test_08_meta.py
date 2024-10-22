# -*- coding: utf8 -*-

import requests

from variables import API_URL, METAS


def test_singouins_meta(jwt_header):
    for meta in METAS:
        response  = requests.get(f'{API_URL}/meta/item/{meta}', headers=jwt_header['access'])
        assert response.status_code == 200
        assert response.json().get("success") is True
