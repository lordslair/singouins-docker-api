# -*- coding: utf8 -*-

import json
import os
import redis
import time
import yarqueue


# Redis variables
REDIS_HOST = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)
REDSUB_QUEUE = os.environ.get('REDSUB_QUEUE', 'yarqueue:discord')

r_no_decode = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_NAME,
    encoding='utf-8',
    )

yqueue = yarqueue.Queue(name=REDSUB_QUEUE, redis=r_no_decode)


def test_redis_expire():
    """
    Expiring a key with this pattern should trigger the redsub script
    We should be able to fetch an item inserted in the REDSUB_QUEUE queue
    Expected:
    {
        "ciphered": False,
        "payload": {
            "creatureuuid": CREATURE_UUID,
            "data": DATA,
            "fullkey": FULLKEY,
            "instanceuuid": INSTANCE_UUID,
            "type": TYPE,
            },
        "embed": None,
        "scope": None,
        "source": 'redsub',
        }
    """
    INSTANCE_UUID = "00000000-0000-0000-0000-000000000000"
    CREATURE_UUID = "11111111-1111-1111-1111-111111111111"
    DATA          = "PyTest"
    TYPE          = "tests"
    FULLKEY       = f'{TYPE}:{INSTANCE_UUID}:{CREATURE_UUID}:{DATA}'
    # We SET the data and EXPIRE
    r_no_decode.set(FULLKEY, '')
    r_no_decode.expire(FULLKEY, 1)
    # We wait EXPIRE and redsub doing its job
    time.sleep(3)
    # We check the item was properly inserted in queue
    assert yqueue.qsize() == 1
    msg_str = yqueue.get()
    assert msg_str is not None
    msg_json = json.loads(msg_str)
    assert msg_json['payload']['creatureuuid'] == CREATURE_UUID
    assert msg_json['payload']['data'] == DATA
    assert msg_json['payload']['fullkey'] == FULLKEY
    assert msg_json['payload']['instanceuuid'] == INSTANCE_UUID
    assert msg_json['payload']['type'] == TYPE
