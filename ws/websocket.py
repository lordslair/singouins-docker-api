#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Inspired from https://github.com/aaugustin/websockets/issues/653

import asyncio
import os
import uuid
import websockets
import yarqueue

from loguru             import logger
from redis              import Redis

# Log System imports
logger.info('[DB:*][core] [✓] System imports')

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB      = os.environ['SEP_REDIS_DB']
REDIS_SLEEP   = float(os.environ['SEP_REDIS_SLEEP'])  # We receive env as STR

# WebSocket variables
WSS_HOST      = os.environ.get('SEP_WSS_HOST', '0.0.0.0')
WSS_PORT      = os.environ.get('SEP_WSS_PORT', 5000)
WSS_QUEUE     = os.environ.get('SEP_WSS_QUEUE', 'broadcast')

# Opening Redis connection
try:
    r = Redis(host=REDIS_HOST,
              port=REDIS_PORT,
              db=REDIS_DB,
              encoding='utf-8',
              socket_connect_timeout=1)
except (Redis.ConnectionError,
        Redis.BusyLoadingError):
    logger.error(f'[DB:{REDIS_DB}][core] '
                 f'[✗] Connection to redis:{REDIS_DB}')
else:
    logger.info(f'[DB:{REDIS_DB}][core] '
                f'[✓] Connection to redis:{REDIS_DB}')

# Opening Queue
try:
    yqueue      = yarqueue.Queue(name=WSS_QUEUE, redis=r)
except Exception as e:
    logger.error(f'[DB:{REDIS_DB}][core] '
                 f'[✗] Connection to Queue {WSS_QUEUE} [{e}]')
else:
    logger.info(f'[DB:{REDIS_DB}][core] '
                f'[✓] Connection to Queue {WSS_QUEUE}')

CLIENTS = set()


async def broadcast():
    while True:
        if not yqueue.empty():
            data = yqueue.get()
            logger.debug(f'[Q:{WSS_QUEUE}] Consumer got from redis:<{data}>')
            await asyncio.gather(
                *[ws.send(data) for ws in CLIENTS],
                return_exceptions=False,
                )

        await asyncio.sleep(REDIS_SLEEP)


async def handler(websocket, path):
    # When client connects
    CLIENTS.add(websocket)
    realip = websocket.request_headers['X-Real-IP']
    ipuuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, realip))
    logger.info(f'[loop] [✓] Client connected (@IP:{realip})')

    # Storing in redis client connlog
    try:
        rkey   = f'wsclients:{str(uuid.uuid4())}'
        r.set(rkey, realip)
    except Exception as e:
        logger.error(f'[loop] [✗] Client logged    (@IP:{realip}) [{e}]')
    else:
        logger.info(f'[loop] [✓] Client logged    (@IP:{realip})')

    # Main loop
    try:
        # Receiving messages
        async for msg in websocket:
            # Queuing them
            yqueue.put(msg)
    except websockets.ConnectionClosedError:
        logger.warning(f'[loop] [✗] Client lost      (@IP:{realip})')
    finally:
        # At the end, we remove the connection
        CLIENTS.remove(websocket)
        # We delete in redis client connlog
        try:
            r.delete(f'wsclients:{ipuuid}')
        except Exception as e:
            logger.error(f'[loop] [✗] Client removed   (@IP:{realip}) [{e}]')
        else:
            logger.info(f'[loop] [✓] Client removed   (@IP:{realip})')

loop = asyncio.get_event_loop()
loop.create_task(broadcast())

# Opening Queue
try:
    start_server = websockets.serve(handler, WSS_HOST, WSS_PORT)
except Exception as e:
    logger.error(f'[core] [✗] Starting websocket [{e}]')
else:
    logger.info(f'[core] [✓] Starting websocket (wss://{WSS_HOST}:{WSS_PORT})')

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
        logger.error(f'[core] [✗] Cleaned wsclients in redis [{e}]')
    else:
        logger.info('[core] [✓] Cleaned wsclients in redis')
    finally:
        # We can proprerly exit now
        logger.info('[core] [✓] Exiting')
