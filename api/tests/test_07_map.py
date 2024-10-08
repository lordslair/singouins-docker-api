# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    MAP_ID,
    access_token_get,
    )


def test_singouins_map():
    response  = requests.get(
        f'{API_URL}/map/{MAP_ID}',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
