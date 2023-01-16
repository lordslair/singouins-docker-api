# -*- coding: utf8 -*-

import os
import sys

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisMeta import RedisMeta  # noqa: E402

META_ID = 42
META_TYPE = 'armor'


def test_redis_meta_get_ok():
    """
    Querying a RedisMeta
    """
    Meta = RedisMeta(metaid=META_ID, metatype=META_TYPE)

    assert Meta.arm_p == 30
    assert Meta.slot == 'Legs'


def test_redis_meta_get_ko():
    """
    Querying a RedisMeta
    > Expected to fail
    """
    Meta = RedisMeta(metaid=666, metatype=META_TYPE)

    assert hasattr(Meta, 'slot') is False
