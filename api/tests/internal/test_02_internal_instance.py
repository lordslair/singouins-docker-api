# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       HEADERS)


def test_singouins_internal_instances():
    url = f'{API_URL}/internal/instances'
    response = requests.get(url, headers=HEADERS)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert 'Instances Query OK' in json.loads(response.text)['msg']
