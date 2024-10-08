# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    METAS,
    access_token_get,
    )


def test_singouins_meta():
    for meta in METAS:
        response  = requests.get(
            f'{API_URL}/meta/item/{meta}',
            headers={"Authorization": f"Bearer {access_token_get()}"},
            )
        assert response.status_code == 200
        assert json.loads(response.text)['success'] is True
