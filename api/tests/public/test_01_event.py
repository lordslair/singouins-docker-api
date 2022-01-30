# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID)

def test_singouins_public_events():
    url       = f'{API_URL}/pc/{CREATURE_ID}/event'
    response  = requests.get(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
