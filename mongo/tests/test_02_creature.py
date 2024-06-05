# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Creature import CreatureDocument, CreatureHP, CreatureStats, CreatureStatsType, CreatureSquad, CreatureSlots, CreatureKorp  # noqa

CREATURE_NAME = "PyTest Creature"
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
CREATURE_B = 10
CREATURE_G = 20
CREATURE_M = 30
CREATURE_P = 40
CREATURE_R = 50
CREATURE_V = 60
CREATURE_CURRENCY_AMOUNT = 1000
USER_NAME = 'user@exemple.net'
USER_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))


def test_mongodb_creature_new():
    """
    Creating a new CreatureDocument
    """

    newCreature = CreatureDocument(
        _id=uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME),
        account=USER_ID,
        gender=True,
        hp=CreatureHP(
            base=CREATURE_M + 100,
            current=CREATURE_M + 100,
            max=CREATURE_M + 100,
            ),
        korp=CreatureKorp(),
        name=CREATURE_NAME,
        race=4,
        squad=CreatureSquad(),
        slots=CreatureSlots(),
        stats=CreatureStats(
            spec=CreatureStatsType(),
            race=CreatureStatsType(
                b=CREATURE_B,
                g=CREATURE_G,
                m=CREATURE_M,
                p=CREATURE_P,
                r=CREATURE_R,
                v=CREATURE_V,
            ),
            total=CreatureStatsType(
                b=CREATURE_B + 1,
                g=CREATURE_G + 2,
                m=CREATURE_M + 3,
                p=CREATURE_P + 4,
                r=CREATURE_R + 5,
                v=CREATURE_V + 6,
            ),
        ),
    )
    newCreature.instance = None
    newCreature.save()

    assert str(newCreature.id) == CREATURE_ID
    assert newCreature.name == CREATURE_NAME
    assert newCreature.gender is True


def test_mongodb_creature_get_ok():
    """
    Querying a CreatureDocument
    """
    pass


def test_mongodb_creature_search_ok():
    """
    Searching a Creature
    """
    assert CreatureDocument.objects(_id=CREATURE_ID).count() == 1
    assert CreatureDocument.objects(name=CREATURE_NAME).count() == 1

    Creature = CreatureDocument.objects(_id=CREATURE_ID).first()
    print(Creature.to_mongo().to_dict())
    assert str(Creature.id) == CREATURE_ID
