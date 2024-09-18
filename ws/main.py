#!/usr/bin/env python3
# -*- coding: utf8 -*-

import asyncio
import datetime
import json
import redis.asyncio as redis
import os
import websockets

from loguru import logger
from websockets import WebSocketServerProtocol

# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_BASE = int(os.environ.get("REDIS_BASE", 0))
logger.debug(f"REDIS_HOST: {REDIS_HOST}")
logger.debug(f"REDIS_PORT: {REDIS_PORT}")
logger.debug(f"REDIS_BASE: {REDIS_BASE}")
# APP variables
API_ENV = os.environ.get("API_ENV", None)
# PubSub variables
PS_BROADCAST = os.environ.get("PS_BROADCAST", f'ws-broadcast-{API_ENV.lower()}')
PS_EXPIRE = os.environ.get("PS_EXPIRE", '__keyevent@0__:expired')
logger.debug(f"PS_BROADCAST: {PS_BROADCAST}")
logger.debug(f"PS_EXPIRE: {PS_EXPIRE}")
# WebSocket variables
WSS_HOST = os.environ.get('WSS_HOST', '0.0.0.0')
WSS_PORT = int(os.environ.get('WSS_PORT', 5000))
logger.debug(f"WSS_HOST: {WSS_HOST}")
logger.debug(f"WSS_PORT: {WSS_PORT}")

CLIENTS = set()


async def listen_to_broadcast() -> None:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)
    pubsub = r.pubsub()
    await pubsub.subscribe(PS_BROADCAST)

    # Continuously listen for messages
    async for message in pubsub.listen():
        logger.trace(f'Pub/Sub received: {message}')
        if message['type'] == 'message':
            data = message['data'].decode('utf-8')
            # Send the message to all connected WebSocket clients
            await notify_clients(data)


async def listen_to_expired() -> None:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)
    pubsub = r.pubsub()
    await pubsub.psubscribe('__keyevent@0__:expired')

    # Continuously listen for messages
    async for message in pubsub.listen():
        logger.trace(f'Pub/Sub received: {message}')
        if message['type'] == 'pmessage':
            expired_key = message['data'].decode()
            # Check we match the API_ENV
            if expired_key.startswith(API_ENV):
                logger.debug(f"Key expired: {expired_key}")
                # We split the key to grab the elements
                splitted_key = expired_key.split(':')
                # Build the message
                message = json.dumps({
                    "creature": splitted_key[2],
                    "date": datetime.datetime.utcnow().isoformat(),
                    "env": API_ENV,
                    "event": "expired",
                    "key": expired_key,
                    "name": splitted_key[3],
                    "type": splitted_key[1],
                })
                # Send the message to all connected WebSocket clients
                await notify_clients(message)


async def notify_clients(message: str) -> None:
    if CLIENTS:  # asyncio.wait doesn't accept an empty list
        logger.info(f'Broadcasting message to {len(CLIENTS)} clients')
        await asyncio.wait(
            [asyncio.create_task(client.send(message)) for client in CLIENTS]
            )


async def websocket_handler(websocket: WebSocketServerProtocol, path: str) -> None:
    # Register client
    real_ip = websocket.request_headers['X-Real-IP']
    logger.info(f'Client connection OK (@IP:{real_ip})')

    CLIENTS.add(websocket)
    try:
        async for message in websocket:
            logger.trace(f'WS received: {message}')
            pass  # Do nothing with received messages for now
    except websockets.exceptions.ConnectionClosed as e:
        logger.debug(f'Client disconnected (@IP:{real_ip}): {e}')
    finally:
        # Unregister client
        logger.debug(f'Client remove OK (@IP:{real_ip})')
        CLIENTS.remove(websocket)


async def main() -> None:
    # Start WebSocket server
    logger.trace(f'WebSocket server start >> ({WSS_HOST}:{WSS_PORT})')
    ws_server = await websockets.serve(websocket_handler, WSS_HOST, WSS_PORT)
    logger.debug('WebSocket server start OK')
    logger.debug('Asyncio.gather start >>')
    await asyncio.gather(
        ws_server.wait_closed(),
        listen_to_broadcast(),
        listen_to_expired(),
        )


if __name__ == "__main__":
    # Run the server
    logger.info('Server starting...')
    asyncio.run(main())
