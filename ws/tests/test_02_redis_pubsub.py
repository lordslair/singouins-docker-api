# -*- coding: utf8 -*-

import json
import os
import redis
import time


# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_BASE = int(os.environ.get("REDIS_BASE", 0))
# APP variables
API_ENV = os.environ.get("API_ENV", None)
# PubSub variables
PS_BROADCAST = os.environ.get("PS_BROADCAST", f'ws-broadcast-{API_ENV.lower()}')

SENT_MSG = {
    "ciphered": False,
    "payload": None,
    "route": "mypc/{id1}/inventory/item/{id2}/equip/{id3}/{id4}",
    "scope": {
        "id": None,
        "instance_id": "11111111-1111-1111-1111-111111111111",
        "scope": 'broadcast',
        },
    }

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)


def test_pub():
    # We subscribe
    pubsub = r.pubsub()
    pubsub.psubscribe(PS_BROADCAST)
    time.sleep(1)
    msg = pubsub.get_message()

    # We check the pubsub works
    """
    # Should be like this:
    {
        "type":"psubscribe",
        "pattern":None,
        "channel":"ws-broadcast",
        "data":1
        }
    """
    assert msg['type'] == 'psubscribe'
    assert msg['channel'].decode('utf-8') == PS_BROADCAST


def test_sub():
    # We subscribe
    pubsub = r.pubsub()
    pubsub.psubscribe(PS_BROADCAST)
    time.sleep(1)
    msg = pubsub.get_message()

    # We check the pubsub works
    """
    # Should be like this:
    {
        "type":"psubscribe",
        "pattern":None,
        "channel":"ws-broadcast",
        "data":1
        }
    """
    assert msg['type'] == 'psubscribe'
    assert msg['channel'].decode('utf-8') == PS_BROADCAST

    # We send data tu simulate a creature pop
    r.publish(PS_BROADCAST, json.dumps(SENT_MSG))

    # We check the item was properly published and received
    msg = pubsub.get_message()
    assert msg['type'] == 'pmessage'
    assert msg['channel'].decode('utf-8') == PS_BROADCAST
    assert msg['data'].decode('utf-8') == json.dumps(SENT_MSG)
