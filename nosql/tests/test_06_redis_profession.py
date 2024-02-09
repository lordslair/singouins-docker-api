# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisProfession import RedisProfession  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))


def test_redis_profession_new():
    """
    Creating a new RedisProfession
    """
    Profession = RedisProfession().new(creatureuuid=CREATURE_ID)
    assert Profession.id == CREATURE_ID

    Profession.incr(field='skinning', count=11)
    assert Profession.skinning == 11


def test_redis_profession_get_ok():
    """
    Querying a RedisProfession
    """
    Profession = RedisProfession(creatureuuid=CREATURE_ID).load()

    assert Profession.id == CREATURE_ID
    assert Profession.skinning == 11


def test_redis_profession_search_ok():
    """
    Searching a RedisProfession
    """
    Professions = RedisSearch().profession(query='@skinning:[11 11]')

    Profession = Professions.results_as_dict[0]
    assert Profession['id'] == CREATURE_ID

    Profession = Professions.results[0]
    assert Profession.id == CREATURE_ID


def test_redis_profession_del():
    """
    Removing a RedisProfession
    """
    ret = RedisProfession(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_profession_get_ko():
    """
    Querying a RedisProfession
    > Expected to fail
    """
    Profession = RedisProfession(creatureuuid=CREATURE_ID).load()
    assert hasattr(Profession, 'skinning') is False

    Profession = RedisProfession()
    assert hasattr(Profession, 'skinning') is False


def test_redis_profession_search_empty():
    """
    Searching a RedisProfession
    > Expected to fail
    """
    Professions = RedisSearch().profession(query='@skinning:0')

    assert len(Professions.results) == 0
