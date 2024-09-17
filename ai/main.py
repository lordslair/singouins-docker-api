#!/usr/bin/env python3
# -*- coding: utf8 -*-

import json
import os
import threading

from loguru import logger
from mongoengine import Q

from bestiaire import (
    Salamander,
    Fungus
    )

from mongo.models.Creature import CreatureDocument

from nosql.connector import r, redis
from utils.actions import creature_init, creature_kill, creature_pop
from utils.requests import resolver_generic_request_get

from variables import (
    CREATURE_PATH,
    INSTANCE_PATH,
    RESOLVER_CHECK_SKIP,
    RESOLVER_URL,
    )

# Log System imports
logger.info('[core] System imports OK')

# Pre-flight check for Resolver connection
if os.environ.get("CI"):
    pass
elif RESOLVER_CHECK_SKIP:
    pass
else:
    try:
        ret = resolver_generic_request_get(
            path="/check"
        )
    except Exception as e:
        logger.error(f'[core] >> Resolver KO ({RESOLVER_URL}) [{e}]')
        exit()
    else:
        if ret and ret['success'] is True:
            logger.info(f'[core] >> Resolver OK ({RESOLVER_URL})')
        else:
            logger.warning(f'[core] >> Resolver KO ({RESOLVER_URL})')

# Subscriber pattern
SUB_PATHS = [CREATURE_PATH, INSTANCE_PATH]

# Opening Redis connection
try:
    pubsub = r.pubsub()
except (redis.Redis.ConnectionError,
        redis.Redis.BusyLoadingError) as e:
    logger.error(f'[core] >> Redis KO [{e}]')
else:
    logger.info('[core] >> Redis OK')

# Starting subscription
for path in SUB_PATHS:
    try:
        logger.trace(f'[core] Subscribe to Redis:"{path}" >>')
        pubsub.psubscribe(path)
    except Exception as e:
        logger.error(f'[core] Subscribe to Redis:"{path}" KO [{e}]')
    else:
        logger.info(f'[core] Subscribe to Redis:"{path}" OK')

if __name__ == '__main__':
    # List to store threads
    threads = []

    # Initialize the Threads with existing Creatures in DB
    creature_init()

    # We receive the events from Redis
    for msg in pubsub.listen():
        # We expect something like this as message
        """
        {
          "channel": <ai-{creature|instance}>,
          "data": {
            "action": <pop|kill>,
            "creature": <CreatureDocument.to_json()>
            },
          "pattern": <ai-{creature|instance}>,
          "type": "pmessage",
        }
        """

        if msg['type'] != 'pmessage':
            logger.trace(f"Message receive do not contains a pmessage ({msg})")
            continue
        else:
            data = json.loads(msg['data'])

        if msg['channel'] == CREATURE_PATH:
            if data['action'] == 'pop':
                creature_pop(data['creature'], threads)
            elif data['action'] == 'kill':
                creature_kill(data['creature'], threads)
            elif data['action'] == 'update':
                # Some shit happened to a Creature - need to update thread info
                pass
        else:
            logger.warning(f"Message unknown (data:{data})")
