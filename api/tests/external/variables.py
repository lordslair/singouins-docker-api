# -*- coding: utf8 -*-

import json
import os
import redis
import requests
import uuid

GUNICORN_PORT   = os.environ.get("GUNICORN_PORT", 5000)
API_ENV         = os.environ.get("API_ENV", 5000)
API_URL         = f'http://127.0.0.1:{GUNICORN_PORT}'

# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_BASE = os.environ.get("REDIS_BASE", 0)

r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_BASE,
    encoding='utf-8',
    )

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
