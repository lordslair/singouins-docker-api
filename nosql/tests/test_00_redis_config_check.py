# -*- coding: utf8 -*-

import os
import sys

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.connector import r  # noqa: E402
from nosql.initialize import initialize_redis_indexes  # noqa: E402

# We setup some stuff for later
initialize_redis_indexes()


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


def test_redis_indexes():
    """
    Checking the correctly built indexes from initialize_redis_indexes()
    """
    for index in [
        'cd_idx',
        'effect_idx',
        'status_idx',
    ]:
        info = r.ft(index).info()
        assert info is not None
        assert info['index_name'] == index
