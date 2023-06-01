#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Inspired from https://github.com/aaugustin/websockets/issues/653

import asyncio
import json
import os
import re
import uuid
import websockets

from loguru                     import logger

from nosql.connector            import r

# Log System imports
logger.info('[core] System imports OK')

# Redis variables
REDIS_SLEEP = float(os.environ.get('REDIS_SLEEP', "0.1"))  # We receive a STR

# WebSocket variables
WSS_HOST  = os.environ.get('WSS_HOST', '0.0.0.0')
WSS_PORT  = os.environ.get('WSS_PORT', 5000)
# Redus PubSub variables
PUBSUB_PATH  = os.environ.get('PUBSUB_PATH', '*')

CLIENTS = set()

# Starting subscription
try:
    pubsub = r.pubsub()
    pubsub.psubscribe(PUBSUB_PATH)
except Exception as e:
    logger.error(f'[core] Subscription to Redis:"{PUBSUB_PATH}" KO [{e}]')
else:
    logger.info(f'[core] Subscription to Redis:"{PUBSUB_PATH}" OK')


async def broadcast():
    while True:
        logger.trace(('[loop] Consumer getting pubsub new messages'))
        msg = pubsub.get_message()
        if msg:
            logger.debug(f'[loop] Consumer got <{msg}>')

            # Detect the action which triggered the event
            m = re.search(r"__keyevent@\w__:(?P<action>\w+)", msg['channel'])
            if m is None:
                # No action detected, we skip processing
                logger.trace(
                    f"Regex ?P<action> KO (channel:{msg['channel']}) - Skip"
                    )
                continue

            if m.group('action') == 'expired':
                # Here we get the EXPIRED KEYS
                cplx_key = re.search(
                    (
                        r"(?P<key_root>[a-zA-Z]+):"
                        r"(?P<key_uuid>[a-f0-9]{8}-[a-f0-9]{4}"
                        r"-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}):"
                        r"(?P<key_string>[a-zA-Z]+)$"
                        ),
                    msg['data']
                    )
                await asyncio.gather(
                    *[ws.send(
                        json.dumps({
                            "ciphered": False,
                            "payload": {
                                "type": cplx_key.group('key_root'),
                                "data": cplx_key.group('key_string'),
                                "creatureuuid": cplx_key.group('key_uuid'),
                                "fullkey": msg['data'],
                                },
                            "embed": None,
                            "scope": None,
                            "source": 'redsub',
                            })
                        ) for ws in CLIENTS],
                    return_exceptions=False,
                    )


async def handler(websocket, path):
    # When client connects
    CLIENTS.add(websocket)
    realip = websocket.request_headers['X-Real-IP']
    ipuuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, realip))
    logger.info(f'[loop] Client connection OK (@IP:{realip})')

    # Storing in redis client connlog
    try:
        rkey   = f'wsclients:{str(uuid.uuid4())}'
        r.set(rkey, realip)
    except Exception as e:
        logger.error(f'[loop] Client log KO (@IP:{realip}) [{e}]')
    else:
        logger.info(f'[loop] Client log OK (@IP:{realip})')

    # Main loop
    try:
        # Receiving messages
        async for msg in websocket:
            # We do nothing if we receive a msg through WS
            pass
    except websockets.ConnectionClosedError:
        logger.warning(f'[loop] Client lost (@IP:{realip})')
    finally:
        # At the end, we remove the connection
        CLIENTS.remove(websocket)
        # We delete in redis client connlog
        try:
            r.delete(f'wsclients:{ipuuid}')
        except Exception as e:
            logger.error(f'[loop] Client remove KO (@IP:{realip}) [{e}]')
        else:
            logger.info(f'[loop] Client remove OK (@IP:{realip})')

try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(broadcast())
except Exception as e:
    logger.error(f'[core] Start Loop KO [{e}]')
else:
    logger.info('[core] Start Loop OK')


# Opening Queue
try:
    start_server = websockets.serve(handler, WSS_HOST, WSS_PORT)
except Exception as e:
    logger.error(f'[core] Start WS KO (wss://{WSS_HOST}:{WSS_PORT}) [{e}]')
else:
    logger.info(f'[core] Start WS OK (wss://{WSS_HOST}:{WSS_PORT})')

# Looping to daemonize the Queue
try:
    loop.run_until_complete(start_server)
    loop.run_forever()
except KeyboardInterrupt:
    try:
        # We scan to find the connected clients
        for key in r.scan_iter('wsclients:*'):
            # We loop to delete all the redis entries
            r.delete(key)
    except Exception as e:
        logger.error(f'[core] Cleaned wsclients KO [{e}]')
    else:
        logger.info('[core] Cleaned wsclients OK')
    finally:
        # We can proprerly exit now
        logger.info('[core] Exiting')
