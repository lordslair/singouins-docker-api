# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisCreature import RedisCreature  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))


def test_redis_creature_new():
    """
    Creating a new RedisCreature
    """
    Creature = RedisCreature().new(
        name=CREATURE_NAME,
        raceid=4,
        gender=True,
        accountuuid=ACCOUNT_ID,
        instanceuuid=None,
    )

    assert Creature.name == CREATURE_NAME
    assert Creature.gender is True
    assert Creature.id == CREATURE_ID
    assert Creature.aggro == 0


def test_redis_creature_get_ok():
    """
    Querying a RedisCreature
    """
    Creature = RedisCreature(creatureuuid=CREATURE_ID)

    assert Creature.name == CREATURE_NAME
    assert Creature.gender is True
    assert Creature.id == CREATURE_ID
    assert Creature.aggro == 0


def test_redis_creature_search_ok():
    """
    Searching a Creature
    """
    Creatures = RedisSearch().creature(query=f'@name:{CREATURE_NAME}')

    Creature = Creatures.results_as_dict[0]
    assert Creature['name'] == CREATURE_NAME
    assert Creature['gender'] is True
    assert Creature['id'] == CREATURE_ID
    assert Creature['aggro'] == 0

    Creature = Creatures.results[0]
    assert Creature.name == CREATURE_NAME
    assert Creature.gender is True
    assert Creature.id == CREATURE_ID
    assert Creature.aggro == 0


def test_redis_creature_setters():
    """
    Querying a RedisCreature, and modifiy attributes
    """
    Creature = RedisCreature(creatureuuid=CREATURE_ID)

    Creature.x = 10
    Creature.y = 10

    # Lets check by calling again a Creature if it was updated in Redis
    CreatureAgain = RedisCreature(creatureuuid=CREATURE_ID)

    assert CreatureAgain.x == 10
    assert CreatureAgain.y == 10

    # Lets check that setters through RediSearch are working
    Creatures = RedisSearch().creature(query=f'@name:{CREATURE_NAME}')
    Creature = Creatures.results[0]

    Creature.x = 5
    Creature.y = 5

    CreatureAgain = RedisCreature(creatureuuid=CREATURE_ID)

    assert CreatureAgain.x == 5
    assert CreatureAgain.y == 5


def test_redis_creature_del():
    """
    Removing a RedisCreature
    """
    ret = RedisCreature(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_creature_get_ko():
    """
    Querying a RedisCreature
    > Expected to fail
    """
    Creature = RedisCreature(creatureuuid=CREATURE_ID)

    assert Creature.hkey == 'creatures'
    assert hasattr(Creature, 'rarity') is False
    assert hasattr(Creature, 'name') is False

    Creature = RedisCreature()

    assert Creature.hkey == 'creatures'
    assert hasattr(Creature, 'rarity') is False
    assert hasattr(Creature, 'name') is False


def test_redis_creature_search_empty():
    """
    Searching a Creature
    > Expected to fail
    """
    Creatures = RedisSearch().creature(query=f'@name:{CREATURE_NAME}')

    assert len(Creatures.results) == 0
