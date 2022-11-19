# -*- coding: utf8 -*-

import os
import uuid

GUNICORN_PORT      = os.environ.get("GUNICORN_PORT", 5000)
API_URL            = f'http://127.0.0.1:{GUNICORN_PORT}'
API_INTERNAL_TOKEN = os.environ['SEP_INTERNAL_TOKEN']
HEADERS            = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}

# Creature ID variables
# The CREATURE_ID is supposed to be built with
# uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME)
# if not, almost all /internal tests will fail
CREATURE_NAME   = 'PJTest'
CREATURE_ID     = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
KORP_ID         = '00000000-babe-babe-babe-000000000000'
METAS           = ['armor', 'weapon', 'race']
SQUAD_ID        = 0
USER_NAME       = 'user@exemple.com'
USER_ID         = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))
ITEM_ID         = '00000000-deed-deed-deed-000000000000'

# Effect
EFFECT_NAME     = 'EffectOne'
EFFECT_JSON     = {
    "duration": 300,
    "extra": {
        "extrakey": 'extravalue'
    },
    "source": 1
}

# Status
STATUS_NAME     = 'Poisoned'
STATUS_JSON     = {
    "duration": 300,
    "extra": {
        "extrakey": 'extravalue'
    },
    "source": 1
}

# Skill/CD
SKILL_NAME      = 'Bloodstrike'
SKILL_JSON      = {
    "duration": 300,
    "extra": {
        "extrakey": 'extravalue'
    },
    "source": 1
}
