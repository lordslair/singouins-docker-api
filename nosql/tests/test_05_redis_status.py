# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisStatus import RedisStatus  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))
INSTANCE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'PyTest Instance'))
STATUS_NAME    = "PyTest Status"


def test_redis_status_new():
    """
    Creating a new RedisStatus
    """
    Status = RedisStatus(creatureuuid=CREATURE_ID).new(
        duration_base=180,
        extra=None,
        instance=INSTANCE_ID,
        name=STATUS_NAME,
        source=CREATURE_ID,
    )

    assert Status.name == STATUS_NAME
    assert Status.bearer == CREATURE_ID
    assert Status.source == CREATURE_ID
    assert Status.instance == INSTANCE_ID
    assert Status.duration_base > 0


def test_redis_status_search_ok():
    """
    Searching a Status
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Statuses = RedisSearch().status(query=f'@bearer:{bearer}')

    Status = Statuses.results_as_dict[0]
    assert Status['name'] == STATUS_NAME
    assert Status['bearer'] == CREATURE_ID
    assert Status['source'] == CREATURE_ID
    assert Status['instance'] == INSTANCE_ID
    assert Status['duration_base'] > 0

    Status = Statuses.results[0]
    assert Status.name == STATUS_NAME
    assert Status.bearer == CREATURE_ID
    assert Status.source == CREATURE_ID
    assert Status.instance == INSTANCE_ID
    assert Status.duration_base > 0


def test_redis_status_del():
    """
    Removing a RedisStatus
    """
    ret = RedisStatus(creatureuuid=CREATURE_ID).destroy(name=STATUS_NAME)

    assert ret is True


def test_redis_status_get_ko():
    """
    Querying a RedisStatus
    > Expected to fail
    """
    Status = RedisStatus(creatureuuid=CREATURE_ID, name=STATUS_NAME)

    assert Status.hkey == 'statuses'
    assert hasattr(Status, 'name') is False

    Status = RedisStatus()

    assert Status.hkey == 'statuses'
    assert hasattr(Status, 'name') is False


def test_redis_status_search_empty():
    """
    Searching a Status
    > Expected to fail
    """
    Status = RedisSearch().status(query=f'@name:{STATUS_NAME}')

    assert len(Status.results) == 0
