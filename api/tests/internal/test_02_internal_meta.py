# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS,
                       METAS)

def test_singouins_internal_meta():
    for meta in METAS:
        url      = f'{API_URL}/internal/meta/{meta}' # GET
        response = requests.get(url, headers=HEADERS)

        assert response.status_code == 200
        assert json.loads(response.text)['success'] == True
