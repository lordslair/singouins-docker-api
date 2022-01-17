# -*- coding: utf8 -*-

import json
import requests

from variables import *

def test_singouins_internal_creature_equipment():
    url       = API_URL + '/internal/creature/equipment'
    payload   = {"creatureid": 1}
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.post(url, headers=headers, json = payload)

    assert response.status_code == 200
