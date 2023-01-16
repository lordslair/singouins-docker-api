# -*- coding: utf8 -*-

import os
import sys

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

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
