# -*- coding: utf8 -*-

import os

API_PORT           = os.environ['GUNICORN_PORT']
API_URL            = f'http://127.0.0.1:{API_PORT}'

AUTH_PAYLOAD       = {'username': 'user@exemple.com', 'password': 'plop'}
CREATURE_ID        = 1
MAP_ID             = 1
METAS              = ['armor','weapon','race','effect','skill','status']
PC_NAME            = 'PJTest'
