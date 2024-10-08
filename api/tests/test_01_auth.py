# -*- coding: utf8 -*-

import json
import requests

from variables import (
    AUTH_PAYLOAD,
    API_URL,
    USER_NAME,
    access_token_get,
    refresh_token_get,
    )


def test_singouins_auth_register():
    response  = requests.post(
        f'{API_URL}/auth/register',
        json={'password': 'plop', 'mail': USER_NAME},
        )

    assert response.status_code == 201 or \
        'User successfully added' in json.loads(response.text)['msg']


def test_singouins_auth_login():
    response = requests.post(
        f'{API_URL}/auth/login',
        json=AUTH_PAYLOAD,
        )

    assert response.status_code == 200
    assert json.loads(response.text)


def test_singouins_auth_infos():
    response  = requests.get(
        f'{API_URL}/auth/infos',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['logged_in_as'] == USER_NAME


def test_singouins_auth_refresh():
    response  = requests.post(
        f'{API_URL}/auth/refresh',
        headers={"Authorization": f"Bearer {refresh_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['access_token']

# url       = f'{API_URL}/auth/confirm/{token}'  # POST  # NOTDONE
