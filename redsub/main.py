#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Reminder, Redis needs to be set with, at minimum :
# redis-cli> config set notify-keyspace-events s$xE

import json
import os
import re
import yarqueue

from loguru                     import logger

from nosql.connector            import r, REDIS_DB_NAME

# Log System imports
logger.info('[core] System imports OK')

# Subscriber pattern
SUB_PATH     = os.environ.get('REDSUB_PATH', '*')
REDSUB_QUEUE = os.environ.get('REDSUB_QUEUE', 'yarqueue:discord')

# Check Redis config
try:
    config = r.config_get(pattern='notify-keyspace-events')
    if config is None or config != '':
        r.config_set(name='notify-keyspace-events', value='$sxE')
except Exception as e:
    logger.error(f'[core] Redis SET notify-keyspace-events KO [{e}]')
else:
    logger.debug('[core] Redis SET notify-keyspace-events OK')

# Opening Queue
try:
    yqueue = yarqueue.Queue(name=REDSUB_QUEUE, redis=r)
except Exception as e:
    logger.error(f'[core] Connection to Queue {REDSUB_QUEUE} KO [{e}]')
else:
    logger.info(f'[core] Connection to Queue {REDSUB_QUEUE} OK')

# Starting subscription
try:
    pubsub = r.pubsub()
    pubsub.psubscribe(SUB_PATH)
except Exception as e:
    logger.error(f'[core] Subscription to Redis:"{SUB_PATH}" KO [{e}]')
else:
    logger.info(f'[core] Subscription to Redis:"{SUB_PATH}" OK')

# We receive the events from Redis
for msg in pubsub.listen():
    logger.trace(f'[PUBSUB][DB:{REDIS_DB_NAME}] {msg}')

    # Detect the action which triggered the event, and related Redis key
    m = re.search(r"__keyevent@\w__:(?P<action>\w+)", msg['channel'])
    if m is None:
        # If no action detected, we skip processing
        logger.trace(
            f"Regex ?P<action> KO (channel:{msg['channel']}) - Skipping"
            )
        continue

    if m.group('action') == 'expired':
        # Here we get the EXPIRED KEYS
        logger.debug(f"[PUBSUB][DB:{REDIS_DB_NAME}] Expired: {msg['data']}")
        # Key that can expire (so far):
        # - Event
        std_key = re.search(
            (
                r"(?P<key_root>[a-zA-Z]+):"
                r"(?P<key_uuid>[a-f0-9]{8}-[a-f0-9]{4}"
                r"-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})$"
                ),
            msg['data']
            )
        # - PA
        # Effect/Status/CD
        cplx_key = re.search(
            (
                r"(?P<key_root>[a-zA-Z]+):"
                r"(?P<key_uuid>[a-f0-9]{8}-[a-f0-9]{4}"
                r"-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}):"
                r"(?P<subkey_uuid>[a-f0-9]{8}-[a-f0-9]{4}"
                r"-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}):"
                r"(?P<key_string>[a-zA-Z]+)$"
                ),
            msg['data']
            )

        if std_key:
            type = std_key.group('key_root')
            creatureuuid = std_key.group('key_uuid')
        elif cplx_key:
            type = cplx_key.group('key_root')
            instanceuuid = cplx_key.group('key_uuid')
            creatureuuid = cplx_key.group('subkey_uuid')
            data = cplx_key.group('key_string')
            qmsg = {
                "ciphered": False,
                "payload": {
                    "type": type,
                    "instanceuuid": instanceuuid,
                    "data": data,
                    "creatureuuid": creatureuuid,
                    "fullkey": msg['data'],
                    },
                "embed": None,
                "scope": None,
                "source": 'redsub',
                }
            logger.success(qmsg)
        else:
            logger.trace(f"RegEx <key_root> KO : {msg['data']}")

        # Put data in Queue
        if qmsg:
            try:
                yqueue.put(json.dumps(qmsg))
            except Exception as e:
                logger.error(
                    f'Queue Query KO '
                    f'(queue:{REDSUB_QUEUE},msg:<{msg}>) [{e}]'
                    )
            else:
                logger.trace(f'Queue Query OK: (qmsg:{qmsg})')
