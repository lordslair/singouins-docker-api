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
    # We start so check&set if necessary (mostly for CI)
    config = r.config_get(pattern='notify-keyspace-events')

    if config is None or config != '':
        ret = r.config_set(name='notify-keyspace-events', value='$sxE')
    assert ret is True

    # We check it again
    config = r.config_get(pattern='notify-keyspace-events')
    assert config is not None
    assert config is not False
    assert config['notify-keyspace-events'] == '$sxE'
