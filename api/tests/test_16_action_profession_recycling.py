# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID


def test_singouins_profession_recycling(jwt_header, myitems):
    # We need the Machette à bananes (metaid:11)
    weapon = [x for x in myitems['weapon'] if x['metaid'] == 11][0]

    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/action/profession/recycling/{weapon['_id']}", headers=jwt_header['access'])  # noqa: E501
    assert response.status_code == 200
    assert response.json().get("success") is True
