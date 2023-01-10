#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Inspired from https://github.com/aaugustin/websockets/issues/653

import asyncio
import os
import uuid
import websockets
import yarqueue

from loguru                     import logger

from nosql.connector            import r_no_decode

# Log System imports
logger.info('[core] System imports OK')

# Redis variables
REDIS_SLEEP = float(os.environ.get('REDIS_SLEEP', "0.1"))  # We receive a STR

# WebSocket variables
WSS_HOST  = os.environ.get('WSS_HOST', '0.0.0.0')
WSS_PORT  = os.environ.get('WSS_PORT', 5000)
WSS_QUEUE = os.environ.get('WSS_QUEUE', 'broadcast')

# Opening Queue
try:
    yqueue = yarqueue.Queue(name=WSS_QUEUE, redis=r_no_decode)
except Exception as e:
    logger.error(f'[core] Connection to Queue {WSS_QUEUE} KO [{e}]')
else:
    logger.info(f'[core] Connection to Queue {WSS_QUEUE} OK')

CLIENTS = set()


async def broadcast():
    while True:
        logger.trace((f'[Q:{WSS_QUEUE}] New loop to check yqueue.empty()'))
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
    logger.info(f'[loop] Client connection OK (@IP:{realip})')

    # Storing in redis client connlog
    try:
        rkey   = f'wsclients:{str(uuid.uuid4())}'
        r_no_decode.set(rkey, realip)
    except Exception as e:
        logger.error(f'[loop] Client log KO (@IP:{realip}) [{e}]')
    else:
        logger.info(f'[loop] Client log OK (@IP:{realip})')

    # Main loop
    try:
        # Receiving messages
        async for msg in websocket:
            # Queuing them
            yqueue.put(msg)
    except websockets.ConnectionClosedError:
        logger.warning(f'[loop] Client lost (@IP:{realip})')
    finally:
        # At the end, we remove the connection
        CLIENTS.remove(websocket)
        # We delete in redis client connlog
        try:
            r_no_decode.delete(f'wsclients:{ipuuid}')
        except Exception as e:
            logger.error(f'[loop] Client remove KO (@IP:{realip}) [{e}]')
        else:
            logger.info(f'[loop] Client remove OK (@IP:{realip})')

loop = asyncio.get_event_loop()
loop.create_task(broadcast())

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
        for key in r_no_decode.scan_iter('wsclients:*'):
            # We loop to delete all the redis entries
            r_no_decode.delete(key)
    except Exception as e:
        logger.error(f'[core] Cleaned wsclients KO [{e}]')
    else:
        logger.info('[core] Cleaned wsclients OK')
    finally:
        # We can proprerly exit now
        logger.info('[core] Exiting')
