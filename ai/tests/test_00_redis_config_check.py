# -*- coding: utf8 -*-

import os
import redis


# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_BASE = os.environ.get("REDIS_BASE", 0)

r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_BASE,
    encoding='utf-8',
    )


def test_redis_ping():
    assert r.ping()
