# -*- coding: utf8 -*-

import requests

from variables import (
    API_ENV,
    API_URL,
    CREATURE_ID,
    r,
    )


def test_singouins_pa(jwt_header):
    response  = requests.get(f'{API_URL}/mypc/{CREATURE_ID}/pa', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert response.json().get("payload")['blue']['ttnpa'] > 0
    assert response.json().get("payload")['red']['ttnpa'] > 0


def test_singouins_pa_reset():
    r.delete(f"{API_ENV}:pas:{CREATURE_ID}:blue")
    r.delete(f"{API_ENV}:pas:{CREATURE_ID}:red")
