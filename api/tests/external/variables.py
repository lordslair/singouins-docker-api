# -*- coding: utf8 -*-

import os
import uuid

GUNICORN_PORT      = os.environ.get("GUNICORN_PORT", 5000)
API_URL            = f'http://127.0.0.1:{GUNICORN_PORT}'

# Creature ID variables
# The CREATURE_ID is supposed to be built with
# uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME)
# if not, almost all /internal tests will fail
CREATURE_NAME   = 'PJTest'
CREATURE_ID     = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
USER_NAME       = 'user@exemple.com'
USER_ID         = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))
SQUAD_ID        = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

AUTH_PAYLOAD    = {'username': USER_NAME, 'password': 'plop'}
MAP_ID          = 1
METAS           = ['armor', 'weapon', 'race']
