# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisHS import RedisHS  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_redis_highscore_new():
    """
    Creating a new RedisHS
    """
    HighScore = RedisHS(creatureuuid=CREATURE_ID)
    HighScore.incr('test_highscore')

    assert HighScore.id == CREATURE_ID
    assert HighScore.test_highscore == 1


def test_redis_highscore_get_ok():
    """
    Querying a RedisHS
    """
    HighScore = RedisHS(creatureuuid=CREATURE_ID)

    assert HighScore.id == CREATURE_ID


def test_redis_cd_search_ok():
    """
    Searching a RedisHS
    """
    pass


def test_redis_highscore_setters():
    """
    Querying a RedisHS, and modifiy attributes
    """
    HighScore = RedisHS(creatureuuid=CREATURE_ID)
    HighScore.incr('test_highscore_count', count=2)

    assert HighScore.test_highscore_count == 2

    # Lets check by calling again a Creature if it was updated in Redis
    HighScoreAgain = RedisHS(creatureuuid=CREATURE_ID)

    assert HighScoreAgain.test_highscore == 1
    assert HighScoreAgain.test_highscore_count == 2


def test_redis_highscore_to_json():
    """
    Querying a RedisHS, and dumping it as JSON
    """
    pass


def test_redis_highscore_del():
    """
    Removing a RedisHS
    """
    ret = RedisHS(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_highscore_del_ko():
    """
    Removing a RedisHS
    > Expected to fail
    """
    ret = RedisHS().destroy()

    assert ret is False


def test_redis_highscore_get_ko():
    """
    Querying a RedisHS
    > Expected to fail
    """
    HighScore = RedisHS(creatureuuid=CREATURE_ID)

    assert HighScore.hkey == 'highscores'
    assert hasattr(HighScore, 'test_highscore') is False
    assert hasattr(HighScore, 'test_highscore_count') is False

    HighScore = RedisHS()

    assert HighScore.hkey == 'highscores'
    assert hasattr(HighScore, 'test_highscore') is False
    assert hasattr(HighScore, 'test_highscore_count') is False


def test_redis_highscore_search_empty():
    """
    Searching a RedisHS
    > Expected to fail
    """
    pass
