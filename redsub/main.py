#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Reminder, Redis needs to be set with, at minimum :
# redis-cli> config set notify-keyspace-events s$xE

import json
import os
import re
import yarqueue

from loguru             import logger
from redis              import Redis

# Log System imports
logger.info('[DB:*][core] [✓] System imports')

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB      = os.environ['SEP_REDIS_DB']
# Subscriber pattern
SUB_PATH      = os.environ['SEP_REDIS_SUB_PATH']
YQUEUE_NAME   = 'yarqueue:discord'

# Opening Redis connection
try:
    r = Redis(host=REDIS_HOST,
              port=REDIS_PORT,
              db=REDIS_DB,
              encoding='utf-8',
              decode_responses=True,
              socket_connect_timeout=1)
except (Redis.ConnectionError,
        Redis.BusyLoadingError):
    logger.error(f'[DB:{REDIS_DB}][core] [✗] Connection to Redis')
else:
    logger.info(f'[DB:{REDIS_DB}][core] [✓] Connection to Redis')

# Opening Queue
try:
    yqueue = yarqueue.Queue(name=YQUEUE_NAME, redis=r)
except Exception as e:
    logger.error(f'Queue Connection KO (queue:{YQUEUE_NAME}) [{e}]')
else:
    pass

# Starting subscription
try:
    pubsub = r.pubsub()
    pubsub.psubscribe(SUB_PATH)
except Exception as e:
    logger.error(f'[DB:{REDIS_DB}][core] '
                 f'[✗] Subscription to Redis:"{SUB_PATH}" [{e}]')
else:
    logger.info(f'[DB:{REDIS_DB}][core] '
                f'[✓] Subscription to Redis:"{SUB_PATH}"')

# We receive the events from Redis
for msg in pubsub.listen():
    logger.trace(f'[DB:{REDIS_DB}] {msg}')

    # Detect the action which triggered the event, and related Redis key
    m = re.search(r"__keyevent@1__:(?P<action>\w+)", msg['channel'])
    if m is None:
        # If no action detected, we skip processing
        logger.trace(f"Regex ?P<action> KO (channel:{msg['channel']})")
        continue
    else:
        logger.trace(f"Regex ?P<action> OK (channel:{msg['channel']})")

    if m.group('action') == 'expired':

        c = re.search(r"(cds):(\d*):(\d*):(\d*):[a-zA-Z0-9_]+",
                      msg['data'])
        s = re.search(r"(status):(\d*):(\d*):(\d*):[a-zA-Z0-9_]+",
                      msg['data'])
        e = re.search(r"(effects):(\d*):(\d*):(\d*):\d*:[a-zA-Z0-9_]+",
                      msg['data'])
        #                           │     │     └────> Regex for {metaid}
        #                           │     └──────────> Regex for {creatureid}
        #                           └────────────────> Regex for {instanceid}

        if c is not None:
            type       = 'CD'
            creatureid = c.group(3)
            metaid     = c.group(4)
        elif s is not None:
            type       = 'Status'
            creatureid = s.group(3)
            metaid     = s.group(4)
        elif e is not None:
            type       = 'Effect'
            creatureid = e.group(3)
            metaid     = e.group(4)
        else:
            # If no action detected, we skip processing
            logger.warning(f"regex ko: {msg['data']}")
            continue

        logger.debug(f"[DB:{REDIS_DB}][expired] {msg['data']}")

        # Put data in Queue
        try:
            qmsg = {"ciphered": False,
                    "payload": {"type":     type,
                                "metaid":   metaid,
                                "creature": creatureid},
                    "embed": None,
                    "scope": None,
                    "source": 'redsub'}
            yqueue.put(json.dumps(qmsg))

        except Exception as e:
            logger.error(f'Queue Query KO '
                         f'(queue:{YQUEUE_NAME},msg:<{msg}>) [{e}]')
        else:
            logger.trace(f'Queue Query OK: (qmsg:{qmsg})')
