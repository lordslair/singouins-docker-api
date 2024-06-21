# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Cosmetic import (  # noqa: E402
    CosmeticData,
    CosmeticDocument,
)

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

COSMETIC = {
    "metaid": 8,
    "data": {
        "hasGender": True,
        "beforeArmor": False,
        "hideArmor": False,
        }
    }


def test_mongodb_cosmetic_new():
    """
    Creating a new CosmeticDocument
    """
    newCosmetic = CosmeticDocument(
        bearer=CREATURE_ID,
        metaid=COSMETIC['metaid'],
        data=CosmeticData(
            beforeArmor=COSMETIC['data']['beforeArmor'],
            hasGender=COSMETIC['data']['hasGender'],
            hideArmor=COSMETIC['data']['hideArmor'],
            )
        )
    newCosmetic.save()

    assert str(newCosmetic.bearer) == CREATURE_ID
    assert newCosmetic.metaid == COSMETIC['metaid']
    assert newCosmetic.data.beforeArmor == COSMETIC['data']['beforeArmor']
    assert newCosmetic.data.hasGender == COSMETIC['data']['hasGender']
    assert newCosmetic.data.hideArmor == COSMETIC['data']['hideArmor']


def test_mongodb_cosmetic_get():
    """
    Querying a CosmeticDocument
    """
    pass


def test_mongodb_cosmetic_search():
    """
    Searching a CosmeticDocument
    """
    assert CosmeticDocument.objects(bearer=CREATURE_ID).count() == 1

    Cosmetic = CosmeticDocument.objects(bearer=CREATURE_ID).get()
    assert str(Cosmetic.bearer) == CREATURE_ID
    assert Cosmetic.metaid == COSMETIC['metaid']
    assert Cosmetic.data.beforeArmor == COSMETIC['data']['beforeArmor']
    assert Cosmetic.data.hasGender == COSMETIC['data']['hasGender']
    assert Cosmetic.data.hideArmor == COSMETIC['data']['hideArmor']


def test_mongodb_cosmetic_del():
    """
    Removing a CosmeticDocument
    """

    Cosmetics = CosmeticDocument.objects(bearer=CREATURE_ID)
    if Cosmetics.count() > 0:
        for Cosmetic in Cosmetics:
            Cosmetic.delete()

    assert CosmeticDocument.objects(bearer=CREATURE_ID).count() == 0
