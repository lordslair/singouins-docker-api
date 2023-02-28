# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisCosmetic import RedisCosmetic  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))


def test_redis_cosmetic_new():
    """
    Creating a new RedisCosmetic
    """
    Cosmetic = RedisCosmetic().new(
        creatureuuid=CREATURE_ID,
        cosmetic_caracs={
            'metaid': 8,
            'data': {
                'hasGender': True,
                'beforeArmor': False,
                'hideArmor': None,
                },
            },
        )

    assert Cosmetic.bearer == CREATURE_ID


def test_redis_cosmetic_get_ok():
    """
    Querying a RedisCosmetic
    """
    Cosmetic = RedisCosmetic().new(
        creatureuuid=CREATURE_ID,
        cosmetic_caracs={
            'metaid': 8,
            'data': {
                'hasGender': True,
                'beforeArmor': False,
                'hideArmor': None,
                },
            },
        )
    CosmeticAgain = RedisCosmetic(cosmeticuuid=Cosmetic.id)

    assert CosmeticAgain.id == Cosmetic.id
    assert Cosmetic.bearer == CREATURE_ID


def test_redis_cosmetic_search_ok():
    """
    Searching a Cosmetic
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Cosmetics = RedisSearch().cosmetic(query=f'@bearer:{bearer}')

    Cosmetic = Cosmetics.results_as_dict[0]
    assert Cosmetic['bearer'] == CREATURE_ID

    Cosmetic = Cosmetics.results[0]
    assert Cosmetic.bearer == CREATURE_ID


def test_redis_cosmetic_del():
    """
    Removing a RedisCosmetic
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Cosmetics = RedisSearch().cosmetic(query=f'@bearer:{bearer}')
    for Cosmetic in Cosmetics.results:
        ret = Cosmetic.destroy()
        assert ret is True


def test_redis_cosmetic_get_ko():
    """
    Querying a RedisCosmetic
    > Expected to fail
    """
    Cosmetic = RedisCosmetic()

    assert Cosmetic.hkey == 'cosmetics'
    assert hasattr(Cosmetic, 'id') is False


def test_redis_cosmetic_search_empty():
    """
    Searching a Cosmetic
    > Expected to fail
    """
    bearer = CREATURE_ID.replace('-', ' ')
    Cosmetics = RedisSearch().cosmetic(query=f'@bearer:{bearer}')

    assert len(Cosmetics.results) == 0
