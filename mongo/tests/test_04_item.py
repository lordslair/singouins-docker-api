# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Item import ItemDocument  # noqa: E402
from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon  # noqa: E402

metaNames = {
    'armor': [doc.to_mongo().to_dict() for doc in MetaArmor.objects()],
    'weapon': [doc.to_mongo().to_dict() for doc in MetaWeapon.objects()],
    'race': [doc.to_mongo().to_dict() for doc in MetaRace.objects()]
}

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

ITEM_META_TYPE = 'weapon'
ITEM_META_ID = 37
ITEM_META = metaNames[ITEM_META_TYPE][ITEM_META_ID]


def test_mongodb_item_new():
    """
    Creating a new ItemDocument
    """
    Item = ItemDocument(
        ammo=ITEM_META['max_ammo'],
        bearer=CREATURE_ID,
        bound=False,
        bound_type='BoE',
        metaid=ITEM_META_ID,
        metatype=ITEM_META_TYPE,
        )
    Item.save()

    assert str(Item.bearer) == CREATURE_ID
    assert Item.ammo == ITEM_META['max_ammo']
    assert Item.metaid == ITEM_META_ID
    assert Item.metatype == ITEM_META_TYPE


def test_mongodb_item_get():
    """
    Querying a ItemDocument
    """
    pass


def test_mongodb_item_search():
    """
    Searching a ItemDocument
    """
    assert ItemDocument.objects(bearer=CREATURE_ID).count() == 1

    Item = ItemDocument.objects(bearer=CREATURE_ID).first()
    assert str(Item.metatype) == ITEM_META_TYPE


def test_mongodb_item_del():
    """
    Removing a ItemDocument
    """
    # This part is handled in the purge tests
    pass
