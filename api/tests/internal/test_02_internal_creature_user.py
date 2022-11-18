# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       USER_ID)


def test_singouins_internal_creature_user():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/user'
    response  = requests.get(url, headers=HEADERS)
    payload   = json.loads(response.text)['payload']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert payload['user'] is not None
    assert payload['user'] is not USER_ID
    assert payload['creature'] is not None
    assert payload['creature']['id'] == CREATURE_ID
