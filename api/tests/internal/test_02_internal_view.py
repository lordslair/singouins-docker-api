# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)

def test_singouins_internal_view():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/view'
    response  = requests.get(url, headers=HEADERS)

    assert json.loads(response.text)['success'] == True
    assert 'View Query OK' in json.loads(response.text)['msg']
    assert response.status_code == 200
