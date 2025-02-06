# -*- coding: utf8 -*-

import os

from loguru import logger

from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon

# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_BASE = int(os.environ.get("REDIS_BASE", 0))
logger.debug(f"REDIS_HOST: {REDIS_HOST}")
logger.debug(f"REDIS_PORT: {REDIS_PORT}")
logger.debug(f"REDIS_BASE: {REDIS_BASE}")

# API variables
SEP_SECRET_KEY = os.environ['SEP_SECRET_KEY']
TOKEN_DURATION = int(os.environ.get("SEP_TOKEN_DURATION", 60))
API_URL = os.environ.get("API_URL", 'http://127.0.0.1:5000')
API_ENV = os.environ.get("API_ENV", None)

# YarQueue variables
YQ_BROADCAST = os.environ.get("YQ_BROADCAST", f'{API_ENV}:yarqueue:broadcast')
YQ_DISCORD   = os.environ.get("YQ_DISCORD", f'{API_ENV}:yarqueue:discord')
# PubSub variables
PS_BROADCAST = os.environ.get("PS_BROADCAST", 'ws-broadcast')

# Discord permanent invite link
DISCORD_URL = os.environ.get("SEP_DISCORD_URL", 'http://127.0.0.1')

# Resolver variables
RESOLVER_HOST = os.environ.get("RESOLVER_HOST", 'resolver-svc')
RESOLVER_PORT = os.environ.get("RESOLVER_PORT", 3000)
RESOLVER_URL  = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'

# Gunicorn variables
GUNICORN_CHDIR   = os.environ.get("GUNICORN_CHDIR", '/code')
GUNICORN_HOST    = os.environ.get("GUNICORN_HOST", "0.0.0.0")
GUNICORN_PORT    = os.environ.get("GUNICORN_PORT", 5000)
GUNICORN_BIND    = f'{GUNICORN_HOST}:{GUNICORN_PORT}'
GUNICORN_WORKERS = os.environ.get("GUNICORN_WORKERS", 1)
GUNICORN_THREADS = os.environ.get("GUNICORN_THREADS", 2)
GUNICORN_RELOAD  = os.environ.get("GUNICORN_RELOAD", True)

# GitHub check to position relative paths correctly
if os.environ.get("CI"):
    # Here we are inside GitHub CI process
    DATA_PATH = 'api/data'
else:
    DATA_PATH = 'data'

# Static data
rarity_levels = {
    'creature': ['Small', 'Medium', 'Big', 'Unique', 'Boss', 'God'],
    'standard': ['Broken', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
}

rarity_array = {
    'creature': rarity_levels['creature'],
    'resource': rarity_levels['standard'],
    'item': rarity_levels['standard'],
}

"""
DISCLAIMER: This is some fat shit I dumped here

This is a HUGE Dictionary to manipulate pore easiliy all the metas
Without having to query MongoDB all the time internally

Do not modifiy unless you're ready for consequences
"""
metaNames = {
    'armor': [doc.to_mongo().to_dict() for doc in MetaArmor.objects()],
    'weapon': [doc.to_mongo().to_dict() for doc in MetaWeapon.objects()],
    'race': [doc.to_mongo().to_dict() for doc in MetaRace.objects()]
}

metaIndexed = {
    'armor': {armor["_id"]: armor for armor in metaNames['armor']},
    'weapon': {weapon["_id"]: weapon for weapon in metaNames['weapon']},
    'race': {race["_id"]: race for race in metaNames['race']},
}
