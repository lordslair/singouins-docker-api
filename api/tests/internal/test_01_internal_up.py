# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS)


def test_singouins_internal_up():
    url       = f'{API_URL}/internal/up'
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
