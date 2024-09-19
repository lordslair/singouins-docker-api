# -*- coding: utf8 -*-

import os
import redis

# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_BASE = int(os.environ.get("REDIS_BASE", 0))
# APP variables
API_ENV = os.environ.get("API_ENV", None)
# PubSub variables
PS_BROADCAST = os.environ.get("PS_BROADCAST", f'ws-broadcast-{API_ENV.lower()}')


def test_redis_ping():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)
    assert r.ping()


def test_redis_config():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)

    try:
        config = r.config_get(pattern='notify-keyspace-events')
        if 'notify-keyspace-events' not in config or config['notify-keyspace-events'] == '':
            r.config_set(name='notify-keyspace-events', value='$sxE')
    except Exception as e:
        print(f'Redis init: notify-keyspace-events KO [{e}]')
    else:
        config = r.config_get(pattern='notify-keyspace-events')
        assert config is not None
        assert config is not False
        assert config['notify-keyspace-events'] == '$sxE'
