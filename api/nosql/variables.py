# -*- coding: utf8 -*-

import os

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

# Redis variables
REDIS_HOST    = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST", 127.0.0.1)
REDIS_PORT    = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)

if os.environ.get("CI"):
    # Here we are inside GitHub CI process
    DATA_PATH   = 'api/data'
else:
    DATA_PATH   = 'data'

# Metafiles location for Redis init
META_FILES = {'armor':  f'{DATA_PATH}/metas/armors.json',
              'effect': f'{DATA_PATH}/metas/effects.json',
              'race':   f'{DATA_PATH}/metas/races.json',
              'skill':  f'{DATA_PATH}/metas/skills.json',
              'status': f'{DATA_PATH}/metas/statuses.json',
              'weapon': f'{DATA_PATH}/metas/weapons.json'}
# Mapfiles location for Redis init
MAP_FILES = {'1': f'{DATA_PATH}/maps/1.json',
             '2': f'{DATA_PATH}/maps/2.json'}
