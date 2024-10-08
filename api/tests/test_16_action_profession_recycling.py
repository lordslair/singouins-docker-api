# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    access_token_get,
    )


def test_singouins_profession_recycling():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons = json.loads(response.text)['payload']['weapon']
    # We need the Machette à bananes (metaid:11)
    weapon = [x for x in weapons if x['metaid'] == 11][0]

    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/action/profession/recycling/{weapon['_id']}",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
