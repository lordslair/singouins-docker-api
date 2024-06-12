# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Aggro import AggroDocument  # noqa: E402
from mongo.models.Creature import CreatureDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

AGGRO_AMOUNT = 100


def test_mongodb_aggro_new():
    """
    Creating a new AggroDocument
    """

    Creature = CreatureDocument.objects(_id=CREATURE_ID).get()

    newAggro = AggroDocument(
        amount=AGGRO_AMOUNT,
        bearer=CREATURE_ID,
        instance=Creature.instance,
        )
    newAggro.save()

    assert str(newAggro.bearer) == CREATURE_ID
    assert newAggro.amount == AGGRO_AMOUNT


def test_mongodb_aggro_get():
    """
    Querying a AggroDocument
    """
    pass


def test_mongodb_aggro_search():
    """
    Searching a Aggro
    """
    assert AggroDocument.objects(bearer=CREATURE_ID).count() == 1

    Aggro = AggroDocument.objects(bearer=CREATURE_ID).get()
    assert str(Aggro.bearer) == CREATURE_ID
    assert Aggro.amount == AGGRO_AMOUNT


def test_mongodb_aggro_del():
    """
    Removing a AggroDocument
    """

    Aggros = AggroDocument.objects(bearer=CREATURE_ID)
    if Aggros.count() > 0:
        for Aggro in Aggros:
            Aggro.delete()

    assert AggroDocument.objects(bearer=CREATURE_ID).count() == 0
