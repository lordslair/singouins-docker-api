# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisEffect import RedisEffect  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))
INSTANCE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'PyTest Instance'))
EFFECT_NAME    = "PyTest Effect"


def test_redis_effect_new():
    """
    Creating a new RedisEffect
    """
    Effect = RedisEffect(creatureuuid=CREATURE_ID).new(
        duration_base=180,
        extra={},
        instance=INSTANCE_ID,
        name=EFFECT_NAME,
        source=CREATURE_ID,
    )

    assert Effect.name == EFFECT_NAME
    assert Effect.bearer == CREATURE_ID
    assert Effect.source == CREATURE_ID
    assert Effect.instance == INSTANCE_ID
    assert Effect.duration_base > 0


def test_redis_effect_search_ok():
    """
    Searching a Effect
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Effects = RedisSearch().effect(query=f'@bearer:{bearer}')

    Effect = Effects.results_as_dict[0]
    assert Effect['name'] == EFFECT_NAME
    assert Effect['bearer'] == CREATURE_ID
    assert Effect['source'] == CREATURE_ID
    assert Effect['instance'] == INSTANCE_ID
    assert Effect['duration_base'] > 0

    Effect = Effects.results[0]
    assert Effect.name == EFFECT_NAME
    assert Effect.bearer == CREATURE_ID
    assert Effect.source == CREATURE_ID
    assert Effect.instance == INSTANCE_ID
    assert Effect.duration_base > 0


def test_redis_effect_del():
    """
    Removing a RedisEffect
    """
    ret = RedisEffect(creatureuuid=CREATURE_ID).destroy(name=EFFECT_NAME)

    assert ret is True


def test_redis_effect_get_ko():
    """
    Querying a RedisEffect
    > Expected to fail
    """
    Effect = RedisEffect(creatureuuid=CREATURE_ID, name=EFFECT_NAME)

    assert Effect.hkey == 'effects'
    assert hasattr(Effect, 'name') is False

    Effect = RedisEffect()

    assert Effect.hkey == 'effects'
    assert hasattr(Effect, 'name') is False


def test_redis_effect_search_empty():
    """
    Searching a Effect
    > Expected to fail
    """
    Effect = RedisSearch().effect(query=f'@name:{EFFECT_NAME}')

    assert len(Effect.results) == 0
