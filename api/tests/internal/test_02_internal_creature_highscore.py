# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)

def test_singouins_internal_view():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/highscore'
    response  = requests.get(url, headers=HEADERS)

    assert json.loads(response.text)['success'] == True
    assert 'HighScores Query OK' in json.loads(response.text)['msg']
    assert response.status_code == 200
    assert json.loads(response.text)['payload']['highscore'] is not None
    assert json.loads(response.text)['payload']['creature']['id'] == CREATURE_ID
