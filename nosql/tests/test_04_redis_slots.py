# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisSlots import RedisSlots  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_redis_slot_new():
    """
    Creating a new RedisSlot
    """
    Slot = RedisSlots().new(creatureuuid=CREATURE_ID)

    assert Slot.id == CREATURE_ID
    assert Slot.holster is None


def test_redis_slot_get_ok():
    """
    Querying a RedisSlots
    """
    Slot = RedisSlots(creatureuuid=CREATURE_ID)

    assert Slot.id == CREATURE_ID
    assert Slot.holster is None


def test_redis_slot_setters():
    """
    Querying a RedisSlots, and modifiy attributes
    """
    # 1. From a direct Query
    Slot = RedisSlots(creatureuuid=CREATURE_ID)

    Slot.holster = '0000-1111-2222-3333'

    assert Slot.holster == '0000-1111-2222-3333'

    # Lets check by calling again a Creature if it was updated in Redis
    SlotAgain = RedisSlots(creatureuuid=CREATURE_ID)

    assert SlotAgain.holster == '0000-1111-2222-3333'


def test_redis_slot_to_json():
    """
    Querying a RedisSlots, and dumping it as JSON
    """
    pass


def test_redis_slot_del():
    """
    Removing a RedisSlots
    """
    ret = RedisSlots(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_slot_del_ko():
    """
    Removing a RedisSlots
    > Expected to fail
    """
    ret = RedisSlots().destroy()

    assert ret is False


def test_redis_slot_get_ko():
    """
    Querying a RedisSlots
    > Expected to fail
    """
    Slot = RedisSlots(creatureuuid=CREATURE_ID)

    assert Slot.hkey == 'slots'
    assert hasattr(Slot, 'holster') is False
    assert hasattr(Slot, 'lefthand') is False

    Slot = RedisSlots()

    assert Slot.hkey == 'slots'
    assert hasattr(Slot, 'holster') is False
    assert hasattr(Slot, 'lefthand') is False
