# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Squad import SquadDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_mongodb_squad_new():
    """
    Creating a new SquadDocument
    """

    newSquad = SquadDocument(
        leader=CREATURE_ID,
        )
    newSquad.save()

    assert str(newSquad.leader) == CREATURE_ID


def test_mongodb_squad_get():
    """
    Querying a SquadDocument
    """
    pass


def test_mongodb_squad_search():
    """
    Searching a SquadDocument
    """
    assert SquadDocument.objects(leader=CREATURE_ID).count() == 1

    Squad = SquadDocument.objects(leader=CREATURE_ID).get()
    assert str(Squad.leader) == CREATURE_ID


def test_mongodb_squad_del():
    """
    Removing a SquadDocument
    """

    Squads = SquadDocument.objects(leader=CREATURE_ID)
    if Squads.count() > 0:
        for Squad in Squads:
            Squad.delete()

    assert SquadDocument.objects(leader=CREATURE_ID).count() == 0
