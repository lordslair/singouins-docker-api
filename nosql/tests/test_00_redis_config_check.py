# -*- coding: utf8 -*-

import os
import sys

sys.path.append(os.path.dirname('/code/'))

from nosql.connector import r  # noqa: E402


def test_redis_ping():
    """
    Checking Redis server status
    """
    assert r.ping()


def test_redis_config():
    """
    Checking CONFIG:notify-keyspace-events
    """
    config = r.config_get(pattern='notify-keyspace-events')
    assert config is not None
    assert config is not False
    assert config['notify-keyspace-events'] == '$sxE'
