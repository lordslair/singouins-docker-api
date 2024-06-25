# -*- coding: utf8 -*-

import datetime
import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Highscore import (  # noqa: E402
    HighscoreDocument,
    HighscoreGeneral,
    HighscoreInternal,
    HighscoreInternalGenericResource,
    HighscoreProfession,
)

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_mongodb_highscore_new():
    """
    Creating a new HighscoreDocument
    """

    newHighscore = HighscoreDocument(
        _id=CREATURE_ID,
        general=HighscoreGeneral(),
        internal=HighscoreInternal(
            fur=HighscoreInternalGenericResource(),
            item=HighscoreInternalGenericResource(),
            leather=HighscoreInternalGenericResource(),
            meat=HighscoreInternalGenericResource(),
            ore=HighscoreInternalGenericResource(),
            shard=HighscoreInternalGenericResource(),
            skin=HighscoreInternalGenericResource(),
            ),
        profession=HighscoreProfession(),
    )
    newHighscore.save()

    assert str(newHighscore.id) == CREATURE_ID
    assert newHighscore.general.kill == 0

    #
    # Update
    #

    highscores_update_query = {
        'inc__general__kill': 10,
        "set__updated": datetime.datetime.utcnow(),
        }
    newHighscore.update(**highscores_update_query)


def test_mongodb_highscore_get():
    """
    Querying a HighscoreDocument
    """
    Highscore = HighscoreDocument.objects(_id=CREATURE_ID).get()

    assert Highscore.general.kill == 10


def test_mongodb_highscore_search():
    """
    Searching a HighscoreDocument
    """
    assert HighscoreDocument.objects(_id=CREATURE_ID).count() == 1


def test_mongodb_highscore_del():
    """
    Removing a HighscoreDocument
    """

    HighscoreDocument.objects(_id=CREATURE_ID).delete()

    assert HighscoreDocument.objects(_id=CREATURE_ID).count() == 0
