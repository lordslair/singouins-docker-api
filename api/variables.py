# -*- coding: utf8 -*-

import os

from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon

# JWT variables
SEP_SECRET_KEY = os.environ['SEP_SECRET_KEY']
TOKEN_DURATION = int(os.environ.get("SEP_TOKEN_DURATION", 60))

# External URL
API_URL = os.environ.get("SEP_API_URL", 'http://127.0.0.1:5000')

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

# YarQueue variables
YQ_BROADCAST = os.environ.get("SEP_YQ_BROADCAST", 'yarqueue:broadcast')
YQ_DISCORD   = os.environ.get("SEP_YQ_DISCORD", 'yarqueue:discord')

# GitHub check to position relative paths correctly
if os.environ.get("CI"):
    # Here we are inside GitHub CI process
    DATA_PATH = 'api/data'
else:
    DATA_PATH = 'data'

# Static data
rarity_array = {
    'creature': [
        'Small',
        'Medium',
        'Big',
        'Unique',
        'Boss',
        'God',
    ],
    'resource': [
        'Broken',
        'Common',
        'Uncommon',
        'Rare',
        'Epic',
        'Legendary',
    ],
    'item': [
        'Broken',
        'Common',
        'Uncommon',
        'Rare',
        'Epic',
        'Legendary',
    ],
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
