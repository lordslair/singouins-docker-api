# -*- coding: utf8 -*-

import json
import os
import requests
import uuid

GUNICORN_PORT   = os.environ.get("GUNICORN_PORT", 5000)
API_URL         = f'http://127.0.0.1:{GUNICORN_PORT}'

# Creature ID variables
# The CREATURE_ID is supposed to be built with
# uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME)
CREATURE_NAME   = 'PJTest'
CREATURE_ID     = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
USER_NAME       = 'user@exemple.net'
USER_ID         = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))
SQUAD_ID        = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

AUTH_PAYLOAD    = {'username': USER_NAME, 'password': 'plop'}
MAP_ID          = 1
METAS           = ['armor', 'weapon', 'race']


def access_token_get():
    try:
        response = requests.post(f'{API_URL}/auth/login', json=AUTH_PAYLOAD)
    except Exception as e:
        print(e)
        return
    else:
        return json.loads(response.text)['access_token']


def refresh_token_get():
    try:
        response = requests.post(f'{API_URL}/auth/login', json=AUTH_PAYLOAD)
    except Exception as e:
        print(e)
        return
    else:
        return json.loads(response.text)['refresh_token']
