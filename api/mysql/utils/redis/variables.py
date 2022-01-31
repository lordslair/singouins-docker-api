# -*- coding: utf8 -*-

import os

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB_NAME = os.environ['SEP_REDIS_DB']

# Metafiles location for Redis init
META_FILES = {'races':   'data/metas/races.json',
              'skills':  'data/metas/skills.json',
              'effects': 'data/metas/effects.json'}
