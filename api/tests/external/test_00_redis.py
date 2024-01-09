# -*- coding: utf8 -*-

import os
import redis
import time

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


def test_singouins_redis_connection():
    assert r.ping()


def test_singouins_redis_set():
    assert r.set('test_singouins', 'OK', ex=1)


def test_singouins_redis_get():
    assert r.get('test_singouins')


def test_singouins_redis_expired():
    time.sleep(1)
    assert not r.get('test_singouins')
