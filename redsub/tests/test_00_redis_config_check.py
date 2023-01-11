# -*- coding: utf8 -*-

import os
import redis


# Redis variables
REDIS_HOST = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)

r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_NAME,
    encoding='utf-8',
    )


def test_redis_ping():
    assert r.ping()


def test_redis_config():
    config = r.config_get(pattern='notify-keyspace-events')
    assert config is not None
    assert config is not False
    assert config['notify-keyspace-events'] == '$sxE'
