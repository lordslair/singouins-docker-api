# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Satchel import (  # noqa: E402
    SatchelDocument,
    SatchelAmmo,
    SatchelCurrency,
    SatchelResource,
    SatchelShard,
)

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_mongodb_satchel_new():
    """
    Creating a new SatchelDocument
    """

    newSatchel = SatchelDocument(
        _id=CREATURE_ID,
        ammo=SatchelAmmo(),
        currency=SatchelCurrency(),
        resource=SatchelResource(),
        shard=SatchelShard(),
        )
    newSatchel.save()

    assert str(newSatchel.id) == CREATURE_ID


def test_mongodb_satchel_get():
    """
    Querying a SatchelDocument
    """
    pass


def test_mongodb_satchel_search():
    """
    Searching a SatchelDocument
    """
    assert SatchelDocument.objects(_id=CREATURE_ID).count() == 1

    Satchel = SatchelDocument.objects(_id=CREATURE_ID).get()
    assert str(Satchel.id) == CREATURE_ID


def test_mongodb_satchel_del():
    """
    Removing a SatchelDocument
    """

    SatchelDocument.objects(_id=CREATURE_ID).delete()

    assert SatchelDocument.objects(_id=CREATURE_ID).count() == 0
