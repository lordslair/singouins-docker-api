#!/usr/bin/env python3
# -*- coding: utf8 -*-

import asyncio
import datetime
import json
import redis.asyncio as redis
import os
import websockets

from loguru import logger
from websockets import ServerConnection

# Grab the environment variables
env_vars = {
    "API_ENV": os.environ.get("API_ENV", None),
    "REDIS_HOST": os.environ.get("REDIS_HOST", '127.0.0.1'),
    "REDIS_PORT": int(os.environ.get("REDIS_PORT", 6379)),
    "REDIS_BASE": int(os.environ.get("REDIS_BASE", 0)),
    "PS_BROADCAST": os.environ.get("PS_BROADCAST", f'ws-broadcast-{os.environ.get("API_ENV", None).lower()}'),  # noqa: E501
    "PS_EXPIRE": os.environ.get("PS_EXPIRE", '__keyevent@0__:expired'),
    "PS_SET": os.environ.get("PS_SET", '__keyevent@0__:set'),
    "WSS_HOST": os.environ.get('WSS_HOST', '0.0.0.0'),
    "WSS_PORT": int(os.environ.get('WSS_PORT', 5000)),
}
# Print the environment variables for debugging
for var, value in env_vars.items():
    logger.debug(f"{var}: {value}")

CLIENTS = set()


async def listen_to_broadcast() -> None:
    r = redis.Redis(host=env_vars['REDIS_HOST'], port=env_vars['REDIS_PORT'], db=env_vars['REDIS_BASE'])  # noqa: E501
    pubsub = r.pubsub()
    await pubsub.subscribe(env_vars['PS_BROADCAST'])

    # Continuously listen for messages
    async for message in pubsub.listen():
        logger.trace(f'Pub/Sub received: {message}')
        if message['type'] == 'message':
            data = message['data'].decode('utf-8')
            # Send the message to all connected WebSocket clients
            await notify_clients(data)


async def listen_to_expired() -> None:
    r = redis.Redis(host=env_vars['REDIS_HOST'], port=env_vars['REDIS_PORT'], db=env_vars['REDIS_BASE'])  # noqa: E501
    pubsub = r.pubsub()
    await pubsub.psubscribe(env_vars['PS_EXPIRE'])

    # Continuously listen for messages
    async for message in pubsub.listen():
        logger.trace(f'Pub/Sub received: {message}')
        if message['type'] == 'pmessage':
            expired_key = message['data'].decode()
            # Check we match the API_ENV
            if expired_key.startswith(env_vars['API_ENV']):
                logger.debug(f"Key expired: {expired_key}")
                # We split the key to grab the elements
                splitted_key = expired_key.split(':')
                # Build the message
                message = json.dumps({
                    "creature": splitted_key[2],
                    "date": datetime.datetime.utcnow().isoformat(),
                    "env": env_vars['API_ENV'],
                    "event": "expired",
                    "key": expired_key,
                    "name": splitted_key[3],
                    "type": splitted_key[1],
                })
                # Send the message to all connected WebSocket clients
                await notify_clients(message)


async def listen_to_set() -> None:
    r = redis.Redis(host=env_vars['REDIS_HOST'], port=env_vars['REDIS_PORT'], db=env_vars['REDIS_BASE'])  # noqa: E501
    pubsub = r.pubsub()
    await pubsub.psubscribe(env_vars['PS_SET'])

    # Continuously listen for messages
    async for message in pubsub.listen():
        logger.trace(f'Pub/Sub received: {message}')
        if message['type'] == 'pmessage':
            set_key = message['data'].decode()
            # Check we match the API_ENV
            if set_key.startswith(env_vars['API_ENV']):
                # We split the key to grab the elements
                splitted_key = set_key.split(':')
                # Build the message
                try:
                    message = json.dumps({
                        "creature": splitted_key[2],
                        "date": datetime.datetime.utcnow().isoformat(),
                        "env": env_vars['API_ENV'],
                        "event": "set",
                        "key": set_key,
                        "name": splitted_key[3],
                        "type": splitted_key[1],
                    })
                    # Send the message to all connected WebSocket clients
                    await notify_clients(message)
                    logger.debug(f"Key set: {set_key}")
                except Exception as e:
                    logger.trace(f"Key format not expected [{e}]")


async def notify_clients(message: str) -> None:
    if CLIENTS:  # asyncio.wait doesn't accept an empty list
        logger.info(f'Broadcasting message to {len(CLIENTS)} clients')
        await asyncio.wait(
            [asyncio.create_task(client.send(message)) for client in CLIENTS]
            )


async def websocket_handler(websocket: ServerConnection, path: str) -> None:
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
    logger.trace(f"WebSocket server start >> ({env_vars['WSS_HOST']}:{env_vars['WSS_PORT']})")
    ws_server = await websockets.serve(websocket_handler, env_vars['WSS_HOST'], env_vars['WSS_PORT'])  # noqa: E501
    logger.debug('WebSocket server start OK')
    logger.debug('Asyncio.gather start >>')
    await asyncio.gather(
        ws_server.wait_closed(),
        listen_to_broadcast(),
        listen_to_expired(),
        listen_to_set(),
        )


if __name__ == "__main__":
    # Run the server
    logger.info('Server starting...')
    asyncio.run(main())
