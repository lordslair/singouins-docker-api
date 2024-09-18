# -*- coding: utf8 -*-

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
PS_EXPIRE = os.environ.get("PS_EXPIRE", '__keyevent@0__:expired')


def test_redis_expire():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)

    INSTANCE_UUID = "00000000-0000-0000-0000-000000000000"
    CREATURE_UUID = "11111111-1111-1111-1111-111111111111"
    DATA          = "PyTest"
    TYPE          = "tests"
    FULLKEY       = f'{TYPE}:{INSTANCE_UUID}:{CREATURE_UUID}:{DATA}'
    # We subscribe
    pubsub = r.pubsub()
    pubsub.psubscribe(PS_EXPIRE)
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
    assert msg['channel'] == PS_EXPIRE
    # We SET the data
    r.set(FULLKEY, '')
    # We check the item was properly created
    """
    # Should be like this:
    {
        "type":"pmessage",
        "pattern":"*",
        "channel":"__keyevent@0__:set",
        "data":"tests:00000000-0000-0000-0000-000000000000:11111111-1111-1111-1111-111111111111:PyTest"
        }
    """
    msg = pubsub.get_message()
    assert msg['type'] == 'pmessage'
    assert msg['channel'] == f'__keyevent@{REDIS_BASE}__:set'
    assert msg['data'] == FULLKEY
    r.expire(FULLKEY, 1)
    # We wait EXPIRE and pubsub doing its job
    time.sleep(3)
    # We check the item was properly expired
    """
    # Should be like this:
    {
        "type":"pmessage",
        "pattern":"*",
        "channel":"__keyevent@0__:expired",
        "data":"tests:00000000-0000-0000-0000-000000000000:11111111-1111-1111-1111-111111111111:PyTest"
        }
    """
    msg = pubsub.get_message()
    assert msg['type'] == 'pmessage'
    assert msg['channel'] == f'__keyevent@{REDIS_BASE}__:expired'
    assert msg['data'] == FULLKEY
