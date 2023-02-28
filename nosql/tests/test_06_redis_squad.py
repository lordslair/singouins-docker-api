# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisSquad import RedisSquad  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))
SQUAD_NAME    = "PyTest Squad"
SQUAD_ID      = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_ID))


def test_redis_squad_new():
    """
    Creating a new RedisSquad
    """
    Squad = RedisSquad().new(creatureuuid=CREATURE_ID)

    assert Squad.leader == CREATURE_ID


def test_redis_squad_get_ok():
    """
    Querying a RedisSquad
    """
    Squad = RedisSquad(squaduuid=SQUAD_ID)

    assert Squad.leader == CREATURE_ID


def test_redis_squad_search_ok():
    """
    Searching a Squad
    """
    id = SQUAD_ID.replace('-', ' ')
    Squads = RedisSearch().squad(query=f'@id:{id}')

    Squad = Squads.results_as_dict[0]
    assert Squad['leader'] == CREATURE_ID

    Squad = Squads.results[0]
    assert Squad.leader == CREATURE_ID


def test_redis_squad_del():
    """
    Removing a RedisSquad
    """
    ret = RedisSquad(squaduuid=SQUAD_ID).destroy()

    assert ret is True


def test_redis_squad_get_ko():
    """
    Querying a RedisSquad
    > Expected to fail
    """
    Squad = RedisSquad(squaduuid=SQUAD_ID)

    assert Squad.hkey == 'squads'
    assert hasattr(Squad, 'name') is False

    Squad = RedisSquad()

    assert Squad.hkey == 'squads'
    assert hasattr(Squad, 'name') is False


def test_redis_squad_search_empty():
    """
    Searching a Squad
    > Expected to fail
    """
    id = SQUAD_ID.replace('-', ' ')
    Squads = RedisSearch().squad(query=f'@id:{id}')

    assert len(Squads.results) == 0
