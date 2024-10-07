# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_ENV,
    API_URL,
    CREATURE_ID,
    access_token_get,
    r,
    )


def test_singouins_pa():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/pa',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert json.loads(response.text)['payload']['blue']['ttnpa'] > 0
    assert json.loads(response.text)['payload']['red']['ttnpa'] > 0


def test_singouins_pa_reset():
    r.delete(f"{API_ENV}:pas:{CREATURE_ID}:blue")
    r.delete(f"{API_ENV}:pas:{CREATURE_ID}:red")
