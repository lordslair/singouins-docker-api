# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    access_token_get,
    )


def test_singouins_public_pc():
    response  = requests.get(
        f'{API_URL}/pc/{CREATURE_ID}',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_public_pc_events():
    response  = requests.get(
        f'{API_URL}/pc/{CREATURE_ID}/event',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_public_pc_item():
    response  = requests.get(
        f'{API_URL}/pc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
