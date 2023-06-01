# -*- coding: utf8 -*-

import json
import os
import redis
import time


# Redis variables
REDIS_HOST = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)
PUBSUB_PATH = os.environ.get('PUBSUB_PATH', 'ai-creature')

INSTANCE_UUID = "00000000-0000-0000-0000-000000000000"
CREATURE_UUID = "11111111-1111-1111-1111-111111111111"
CREATURE = {
    "account": None,
    "aggro": 0,
    "created": "2023-06-01 17:03:48",
    "date": "2023-06-01 17:03:48",
    "gender": True,
    "id": CREATURE_UUID,
    "instance": INSTANCE_UUID,
    "korp": None,
    "korp_rank": None,
    "level": 1,
    "name": "PyTest Creature",
    "race": 14,
    "rarity": "Medium",
    "squad": None,
    "squad_rank": None,
    "targeted_by": None,
    "x": 100,
    "xp": 0,
    "y": 100,
    }
INSTANCE = {
    "creator": CREATURE_UUID,
    "fast": False,
    "hardcore": True,
    "id": INSTANCE_UUID,
    "map": 1,
    "public": True,
    "tick": 3600,
    }

r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_NAME,
    encoding='utf-8',
    decode_responses=True,
    )


def test_creature_pop():
    EXPECTED_MSG = {
        "action": 'pop',
        "instance": INSTANCE,
        "creature": CREATURE,
        }
    # We subscribe
    pubsub = r.pubsub()
    pubsub.psubscribe(PUBSUB_PATH)
    time.sleep(1)
    msg = pubsub.get_message()
    # We check the pubsub works
    """
    # Should be like this:
    {
        "type":"psubscribe",
        "pattern":None,
        "channel":"*",
        "data":1
        }
    """
    assert msg['type'] == 'psubscribe'
    assert msg['channel'] == PUBSUB_PATH
    # We send data tu simulate a creature pop
    r.publish(PUBSUB_PATH, json.dumps(EXPECTED_MSG))
    # We check the item was properly created
    msg = pubsub.get_message()
    assert msg['type'] == 'pmessage'
    assert msg['channel'] == PUBSUB_PATH
    assert msg['data'] == json.dumps(EXPECTED_MSG)


def test_creature_kill():
    EXPECTED_MSG = {
        "action": 'kill',
        "instance": INSTANCE,
        "creature": CREATURE,
        }
    # We subscribe
    pubsub = r.pubsub()
    pubsub.psubscribe(PUBSUB_PATH)
    time.sleep(1)
    msg = pubsub.get_message()
    # We check the pubsub works
    """
    # Should be like this:
    {
        "type":"psubscribe",
        "pattern":None,
        "channel":"*",
        "data":1
        }
    """
    assert msg['type'] == 'psubscribe'
    assert msg['channel'] == PUBSUB_PATH
    # We send data tu simulate a creature pop
    r.publish(PUBSUB_PATH, json.dumps(EXPECTED_MSG))
    # We check the item was properly created
    msg = pubsub.get_message()
    assert msg['type'] == 'pmessage'
    assert msg['channel'] == PUBSUB_PATH
    assert msg['data'] == json.dumps(EXPECTED_MSG)
