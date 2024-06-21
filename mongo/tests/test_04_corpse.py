# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Corpse import CorpseDocument  # noqa: E402
from mongo.models.Creature import CreatureDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

KILLER_ID = str(uuid.uuid4())
INSTANCE_ID = str(uuid.uuid4())


def test_mongodb_corpse_new():
    """
    Creating a new CorpseDocument
    """

    # We need the Creature object to do so
    Creature = CreatureDocument.objects(_id=CREATURE_ID).get()

    newCorpse = CorpseDocument(
        _id=Creature.id,
        account=Creature.account,
        gender=Creature.gender,
        instance=INSTANCE_ID,
        killer=KILLER_ID,
        level=Creature.level,
        name=Creature.name,
        race=Creature.race,
        rarity=Creature.rarity,
        x=Creature.x,
        y=Creature.y,
        )
    newCorpse.save()

    assert str(newCorpse.id) == CREATURE_ID
    assert newCorpse.name == CREATURE_NAME


def test_mongodb_corpse_get():
    """
    Querying a CorpseDocument
    """
    pass


def test_mongodb_corpse_search():
    """
    Searching a CorpseDocument
    """
    assert CorpseDocument.objects(_id=CREATURE_ID).count() == 1

    Corpse = CorpseDocument.objects(_id=CREATURE_ID).get()
    assert str(Corpse.id) == CREATURE_ID
    assert Corpse.name == CREATURE_NAME


def test_mongodb_corpse_del():
    """
    Removing a CorpseDocument
    """

    Corpses = CorpseDocument.objects(_id=CREATURE_ID)
    if Corpses.count() > 0:
        for Corpse in Corpses:
            Corpse.delete()

    assert CorpseDocument.objects(_id=CREATURE_ID).count() == 0
