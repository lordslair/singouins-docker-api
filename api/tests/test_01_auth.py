# -*- coding: utf8 -*-

import json
import sys
import os

code = os.path.dirname(os.environ['FLASK_APP'])
sys.path.append(code)

from app import app

def test_singouins_auth_register():
    route     = '/auth/register'
    response  = app.test_client().post(route, json = {'username': 'user', 'password': 'plop', 'mail': 'mail@exemple.com'})

    assert response.status_code == 201

def test_singouins_auth_login():
    route     = '/auth/login'
    response  = app.test_client().post(route, json = {'username': 'user', 'password': 'plop'})

    assert response.status_code == 200
    assert json.loads(response.data)

def test_singouins_auth_infos():
    route     = '/auth/login'
    response  = app.test_client().post(route, json = {'username': 'user', 'password': 'plop'})
    login     = json.loads(response.data)

    route     = '/auth/infos'
    jwt       = json.loads('{"Authorization": "JWT '+ login['access_token'] + '"}')
    response  = app.test_client().get(route, headers = jwt)
    infos     = json.loads(response.data)

    assert response.status_code == 200
    assert infos['logged_in_as'] == 'user'

def test_singouins_auth_refresh():
    route     = '/auth/login'
    response  = app.test_client().post(route, json = {'username': 'user', 'password': 'plop'})
    login     = json.loads(response.data)

    route     = '/auth/refresh'
    jwt       = json.loads('{"Authorization": "JWT '+ login['refresh_token'] + '"}')
    response  = app.test_client().post(route, headers = jwt)
    refresh   = json.loads(response.data)

    assert response.status_code == 200
    assert refresh['access_token']
