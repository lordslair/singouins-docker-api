# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisPa import RedisPa  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_redis_pa_new():
    """
    Creating a new RedisPa
    """
    pass


def test_redis_pa_get_ok():
    """
    Querying a RedisPa
    """
    Pa = RedisPa(creatureuuid=CREATURE_ID)

    assert Pa.redpa == 16
    assert Pa.bluepa == 8


def test_redis_pa_to_json():
    """
    Querying a RedisPa, and dumping it as JSON
    """
    pass


def test_redis_pa_search_ok():
    """
    Searching a RedisPa
    """
    pass


def test_redis_pa_consume():
    """
    Consuming a RedisPa
    """
    Pa = RedisPa(creatureuuid=CREATURE_ID)

    Pa.consume()
    assert Pa.redpa == 16
    assert Pa.bluepa == 8

    ret = Pa.consume(redpa=3, bluepa=4)
    assert ret is True

    PaAgain = RedisPa(creatureuuid=CREATURE_ID)
    assert PaAgain.redpa == 13
    assert PaAgain.bluepa == 4


def test_redis_pa_del():
    """
    Removing a RedisPa
    """
    ret = RedisPa(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_pa_del_ko():
    """
    Removing a RedisPa
    > Expected to fail
    """
    pass


def test_redis_pa_get_ko():
    """
    Querying a RedisPa
    > Expected to fail
    """
    pass


def test_redis_pa_search_empty():
    """
    Searching a RedisPa
    > Expected to fail
    """
    pass
