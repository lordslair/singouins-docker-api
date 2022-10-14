# -*- coding: utf8 -*-

import os

GUNICORN_PORT      = os.environ.get("GUNICORN_PORT", 5000)
API_URL            = f'http://127.0.0.1:{GUNICORN_PORT}'

AUTH_PAYLOAD       = {'username': 'user@exemple.com', 'password': 'plop'}
CREATURE_ID        = 1
MAP_ID             = 1
METAS              = ['armor', 'weapon', 'race']
PC_NAME            = 'PJTest'
