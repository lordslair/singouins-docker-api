# -*- coding: utf8 -*-

import requests

from variables import (
    AUTH_PAYLOAD,
    API_URL,
    USER_NAME,
    )


def test_singouins_auth_register():
    response = requests.post(f'{API_URL}/auth/register', json={'password': 'plop', 'mail': USER_NAME})  # noqa: E501
    assert response.status_code == 201 or \
        'User successfully added' in response.json().get("msg")


def test_singouins_auth_login():
    response = requests.post(f'{API_URL}/auth/login', json=AUTH_PAYLOAD)
    assert response.status_code == 200
    assert response.json().get("access_token")
    assert response.json().get("refresh_token")


def test_singouins_auth_infos(jwt_header):
    response  = requests.get(f'{API_URL}/auth/infos', headers=jwt_header['access'])
    assert response.status_code == 200
    assert response.json().get("logged_in_as") == USER_NAME


def test_singouins_auth_refresh(jwt_header):
    response  = requests.post(f'{API_URL}/auth/refresh', headers=jwt_header['refresh'])
    assert response.status_code == 200
    assert response.json().get("access_token")


def test_singouins_auth_logout():
    # We do a manual login (no from fixture) to avoid revoking global session token
    response = requests.post(f'{API_URL}/auth/login', json=AUTH_PAYLOAD)
    access_token = response.json().get("access_token")
    access_header = {"Authorization": f"Bearer {access_token}"}

    response = requests.delete(f'{API_URL}/auth/logout', headers=access_header)
    assert response.status_code == 200
    assert response.json().get("access_token")
    assert response.json().get("refresh_token")

    # We check token is revoked and access Unauthorized
    response  = requests.get(f'{API_URL}/auth/infos', headers=access_header)
    assert response.status_code == 401
    assert 'revoked' in response.json().get("msg")

# url       = f'{API_URL}/auth/confirm/{token}'  # POST  # NOTDONE
