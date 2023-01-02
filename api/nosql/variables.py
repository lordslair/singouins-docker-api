# -*- coding: utf8 -*-

import re
import os

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

# Redis variables
REDIS_HOST    = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST",
                               '127.0.0.1')
REDIS_PORT    = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)

if os.environ.get("CI"):
    # Here we are inside GitHub CI process
    DATA_PATH   = 'api/data'
else:
    DATA_PATH   = 'data'

# Metafiles location for Redis init
META_FILES = {
    'armor': f'{DATA_PATH}/metas/armors.json',
    'consumable': f'{DATA_PATH}/metas/consumables.json',
    'race': f'{DATA_PATH}/metas/races.json',
    'recipe': f'{DATA_PATH}/metas/recipes.json',
    'weapon': f'{DATA_PATH}/metas/weapons.json',
}
# Mapfiles location for Redis init
MAP_FILES = {
    '1': f'{DATA_PATH}/maps/1.json',
    '2': f'{DATA_PATH}/maps/2.json'
}


def str2typed(string):
    # BOOLEAN False
    if string == 'False':
        return False
    # BOOLEAN True
    elif string == 'True':
        return True
    # None
    elif string == 'None':
        return None
    # Date
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', string):
        return string
    # INT
    elif string.isdigit():
        return int(string)
    else:
        return string


def typed2str(string):
    # None
    if string is None:
        return 'None'
    # BOOLEAN True
    elif string is True:
        return 'True'
    # BOOLEAN False
    elif string is False:
        return 'False'
    else:
        return string
