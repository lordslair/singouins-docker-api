# -*- coding: utf8 -*-

import os

API_PORT           = os.environ['GUNICORN_PORT']
API_URL            = f'http://127.0.0.1:{API_PORT}'
API_INTERNAL_TOKEN = os.environ['SEP_INTERNAL_TOKEN']

# Creature ID variables
CREATURE_ID   = 1
EFFECTMETA_ID = 1
KORP_ID       = 1
SKILLMETA_ID  = 1
SQUAD_ID      = 1
