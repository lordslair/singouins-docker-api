# -*- coding: utf8 -*-

import json
import requests

from variables import *

def test_singouins_internal_up():
    url       = API_URL + '/internal/up'
    headers   = json.loads('{"Authorization": "Bearer '+ API_INTERNAL_TOKEN + '"}')
    response  = requests.get(url, headers=headers)

    assert response.status_code == 200
