# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisItem import RedisItem  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))
ITEM_CARACS   = {
    "metatype": 'weapon',
    "metaid": 32,
    "bound": True,
    "bound_type": 'BoP',
    "modded": False,
    "mods": None,
    "state": 100,
    "rarity": 'Common'
    }


def test_redis_item_new():
    """
    Creating a new RedisItem
    """
    Item = RedisItem().new(creatureuuid=CREATURE_ID, item_caracs=ITEM_CARACS)

    assert Item.bearer == CREATURE_ID
    assert Item.bound is ITEM_CARACS['bound']


def test_redis_item_get_ok():
    """
    Querying a RedisItem
    """
    Item = RedisItem().new(creatureuuid=CREATURE_ID, item_caracs=ITEM_CARACS)
    ItemAgain = RedisItem(itemuuid=Item.id)

    assert ItemAgain.bearer == CREATURE_ID


def test_redis_item_search_ok():
    """
    Searching a Item
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Items = RedisSearch().item(query=f'@bearer:{bearer}')

    Item = Items.results_as_dict[0]
    assert Item['bearer'] == CREATURE_ID

    Item = Items.results[0]
    assert Item.bearer == CREATURE_ID


def test_redis_item_del():
    """
    Removing a RedisItem
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Items = RedisSearch().item(query=f'@bearer:{bearer}')

    ret = RedisItem(itemuuid=Items.results[0].id).destroy()

    assert ret is True


def test_redis_item_get_ko():
    """
    Querying a RedisItem
    > Expected to fail
    """
    Item = RedisItem(itemuuid=CREATURE_ID)

    assert Item.hkey == 'items'
    assert hasattr(Item, 'name') is False

    Item = RedisItem()

    assert Item.hkey == 'items'
    assert hasattr(Item, 'name') is False


def test_redis_item_search_empty():
    """
    Searching a Item
    > Expected to fail
    """
    id = CREATURE_ID.replace('-', ' ')
    Items = RedisSearch().item(query=f'@id:{id}')

    assert len(Items.results) == 0
