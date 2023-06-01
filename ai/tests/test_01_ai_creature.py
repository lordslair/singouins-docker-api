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
        "instance": 'toto',
        "creature": 'plop',
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
        "pattern":"None",
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
        "instance": 'toto',
        "creature": 'plop',
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
        "pattern":"None",
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
