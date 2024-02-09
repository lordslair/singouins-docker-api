# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisCreature import RedisCreature  # noqa: E402
from nosql.models.RedisCorpse import RedisCorpse  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Corpse"
# CREATURE_ID = ## USELESS as we generate a monster it will be random UUID4
RACE_ID = 13  # Guerrier Salamandre
ACCOUNT_ID = None
INSTANCE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'PyTest Instance'))


def test_redis_creature_new():
    """
    Creating a new RedisCorpse
    """
    Creature = RedisCreature().new(
        name=CREATURE_NAME,
        raceid=15,
        gender=True,
        accountuuid=ACCOUNT_ID,
        instanceuuid=INSTANCE_ID,
    )

    assert Creature.name == CREATURE_NAME
    assert Creature.gender is True

    Corpse = RedisCorpse().new(Creature=Creature)

    assert Corpse.name == CREATURE_NAME
    assert Corpse.gender is True
    assert Corpse.killer is None
    assert hasattr(Corpse, 'aggro') is False


def test_redis_creature_search_ok():
    """
    Searching a Creature
    """
    Corpses = RedisSearch().corpse(query=f'@name:{CREATURE_NAME}')

    Corpse = Corpses.results_as_dict[0]
    assert Corpse['gender'] is True
    assert Corpse['killer'] is None
    assert Corpse['name'] == CREATURE_NAME

    Corpse = Corpses.results[0]
    assert Corpse.gender is True
    assert Corpse.killer is None
    assert Corpse.name == CREATURE_NAME


def test_redis_creature_get_ok():
    """
    Querying a RedisCreature
    """
    Corpses = RedisSearch().corpse(query=f'@name:{CREATURE_NAME}')
    Corpse = RedisCorpse(corpseuuid=Corpses.results[0].id).load()

    assert Corpse.gender is True
    assert Corpse.killer is None
    assert Corpse.name == CREATURE_NAME


def test_redis_creature_del():
    """
    Removing a RedisCreature
    """
    Corpses = RedisSearch().corpse(query=f'@name:{CREATURE_NAME}')
    Corpse = Corpses.results[0]
    ret = RedisCorpse(corpseuuid=Corpse.id).destroy()

    assert ret is True


def test_redis_creature_get_ko():
    """
    Querying a RedisCreature
    > Expected to fail
    """
    Creature = RedisCorpse().load()
    assert hasattr(Creature, 'id') is False
    assert hasattr(Creature, 'name') is False


def test_redis_creature_search_empty():
    """
    Searching a Creature
    > Expected to fail
    """
    Creatures = RedisSearch().corpse(query=f'@name:{CREATURE_NAME}')

    assert len(Creatures.results) == 0
