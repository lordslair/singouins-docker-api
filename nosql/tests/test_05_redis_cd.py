# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisCd import RedisCd  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))
INSTANCE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'PyTest Instance'))
SKILL_NAME    = "PyTest Skill"


def test_redis_cd_new():
    """
    Creating a new RedisCd
    """
    Cd = RedisCd(creatureuuid=CREATURE_ID).new(
        duration_base=180,
        extra={},
        instance=INSTANCE_ID,
        name=SKILL_NAME,
        source=CREATURE_ID,
    )

    assert Cd.name == SKILL_NAME
    assert Cd.bearer == CREATURE_ID
    assert Cd.source == CREATURE_ID
    assert Cd.duration_base > 0


def test_redis_cd_search_ok():
    """
    Searching a Cd
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Cds = RedisSearch().cd(query=f'@bearer:{bearer}')

    Cd = Cds.results_as_dict[0]
    assert Cd['name'] == SKILL_NAME
    assert Cd['bearer'] == CREATURE_ID
    assert Cd['source'] == CREATURE_ID
    assert Cd['instance'] == INSTANCE_ID
    assert Cd['duration_base'] > 0

    Cd = Cds.results[0]
    assert Cd.name == SKILL_NAME
    assert Cd.bearer == CREATURE_ID
    assert Cd.source == CREATURE_ID
    assert Cd.instance == INSTANCE_ID
    assert Cd.duration_base > 0


def test_redis_cd_del():
    """
    Removing a RedisCd
    """
    ret = RedisCd(creatureuuid=CREATURE_ID).destroy(name=SKILL_NAME)

    assert ret is True


def test_redis_cd_get_ko():
    """
    Querying a RedisCd
    > Expected to fail
    """
    Cd = RedisCd(creatureuuid=CREATURE_ID, name=SKILL_NAME)

    assert Cd.hkey == 'cds'
    assert hasattr(Cd, 'name') is False

    Cd = RedisCd()

    assert Cd.hkey == 'cds'
    assert hasattr(Cd, 'name') is False


def test_redis_cd_search_empty():
    """
    Searching a Cd
    > Expected to fail
    """
    Cd = RedisSearch().cd(query=f'@name:{SKILL_NAME}')

    assert len(Cd.results) == 0
