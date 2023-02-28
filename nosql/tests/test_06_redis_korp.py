# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisKorp import RedisKorp  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))
KORP_NAME     = "PyTest Korp"
KORP_ID       = uuid.uuid3(uuid.NAMESPACE_DNS, KORP_NAME)


def test_redis_korp_new():
    """
    Creating a new RedisKorp
    """
    Korp = RedisKorp().new(
        creatureuuid=CREATURE_ID,
        korpname=KORP_NAME,
    )

    assert Korp.name == KORP_NAME
    assert Korp.leader == CREATURE_ID


def test_redis_korp_get_ok():
    """
    Querying a RedisKorp
    """
    Korp = RedisKorp(korpuuid=KORP_ID)

    assert Korp.leader == CREATURE_ID


def test_redis_korp_search_ok():
    """
    Searching a Korp
    """
    Korps = RedisSearch().korp(query=f'@name:{KORP_NAME}')

    Korp = Korps.results_as_dict[0]
    assert Korp['name'] == KORP_NAME
    assert Korp['leader'] == CREATURE_ID

    Korp = Korps.results[0]
    assert Korp.name == KORP_NAME
    assert Korp.leader == CREATURE_ID


def test_redis_korp_del():
    """
    Removing a RedisKorp
    """
    ret = RedisKorp(korpuuid=KORP_ID).destroy()

    assert ret is True


def test_redis_korp_get_ko():
    """
    Querying a RedisKorp
    > Expected to fail
    """
    Korp = RedisKorp(korpuuid=KORP_ID)

    assert Korp.hkey == 'korps'
    assert hasattr(Korp, 'name') is False

    Korp = RedisKorp()

    assert Korp.hkey == 'korps'
    assert hasattr(Korp, 'name') is False


def test_redis_korp_search_empty():
    """
    Searching a Korp
    > Expected to fail
    """
    Korps = RedisSearch().korp(query=f'@name:{KORP_NAME}')

    assert len(Korps.results) == 0
