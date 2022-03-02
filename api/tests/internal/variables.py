# -*- coding: utf8 -*-

import os

GUNICORN_PORT      = os.environ.get("GUNICORN_PORT", 5000)
API_URL            = f'http://127.0.0.1:{GUNICORN_PORT}'
API_INTERNAL_TOKEN = os.environ['SEP_INTERNAL_TOKEN']
HEADERS            = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}

# Creature ID variables
CREATURE_ID   = 1
EFFECTMETA_ID = 1
KORP_ID       = 1
METAS         = ['armor','weapon','race','effect','skill','status']
SKILLMETA_ID  = 1
STATUSMETA_ID   = 11
STATUSMETA_NAME = 'Poisoned'
SQUAD_ID      = 1
