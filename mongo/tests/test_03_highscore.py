# -*- coding: utf8 -*-

import datetime
import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Highscore import HighscoreDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_mongodb_highscore_new():
    """
    Creating a new HighscoreDocument
    """

    HighScores = HighscoreDocument.objects(_id=CREATURE_ID)
    highscores_update_query = {
        'inc__general__kill': 10,
        "set__updated": datetime.datetime.utcnow(),
        }
    HighScores.update(**highscores_update_query)

    assert str(HighScores.id) == CREATURE_ID
    assert HighScores.general.kill == 10


def test_mongodb_highscore_get_ok():
    """
    Querying a HighscoreDocument
    """
    pass


def test_mongodb_highscore_search_ok():
    """
    Searching a HighScore
    """
    assert HighscoreDocument.objects(_id=CREATURE_ID).count() == 1


def test_mongodb_highscore_del_ok():
    """
    Removing a HighscoreDocument
    """

    HighscoreDocument.objects(_id=CREATURE_ID).delete()

    assert HighscoreDocument.objects(src=CREATURE_ID).count() == 0
