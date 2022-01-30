# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID)

def test_singouins_item():
    url       = f'{API_URL}/pc/{CREATURE_ID}/item'
    response  = requests.get(url, headers=headers)

    assert json.loads(response.text)['success'] == True
    assert response.status_code == 200
