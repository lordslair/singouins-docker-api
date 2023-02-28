# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisCreature import RedisCreature  # noqa: E402
from nosql.models.RedisSlots import RedisSlots  # noqa: E402
from nosql.models.RedisStats import RedisStats  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))


def test_redis_stats_new():
    """
    Creating a new RedisStats
    """
    Creature = RedisCreature().new(
        name=CREATURE_NAME,
        raceid=4,
        gender=True,
        accountuuid=ACCOUNT_ID,
        instanceuuid=None,
    )
    RedisSlots().new(creatureuuid=CREATURE_ID)

    Stats = RedisStats().new(Creature=Creature, classid=3)

    assert Stats.hp >= 0
    assert Stats.hp == Stats.hpmax


def test_redis_stats_get_ok():
    """
    Querying a RedisStats
    """
    Stats = RedisStats(creatureuuid=CREATURE_ID)

    assert Stats.hp >= 0
    assert Stats.hp == Stats.hpmax


def test_redis_stats_search_ok():
    """
    Searching a Cosmetic
    """
    pass


def test_redis_stats_del():
    """
    Removing a RedisStats
    """
    ret = RedisStats(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_stats_get_ko():
    """
    Querying a RedisStats
    > Expected to fail
    """
    Stats = RedisStats(creatureuuid=CREATURE_ID)

    assert Stats.hkey == 'stats'
    assert hasattr(Stats, 'hp') is False

    Stats = RedisStats()

    assert Stats.hkey == 'stats'
    assert hasattr(Stats, 'hp') is False


def test_redis_stats_cleanup():
    """
    Removing a RedisCreature
    Removing a RedisSlots
    """
    RedisCreature(creatureuuid=CREATURE_ID).destroy()
    RedisSlots(creatureuuid=CREATURE_ID).destroy()
