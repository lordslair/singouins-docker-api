# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    access_token_get,
    )


def test_singouins_item():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
