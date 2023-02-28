# -*- coding: utf8 -*-

import json
import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisSearch import RedisSearch  # noqa: E402
from nosql.models.RedisUser import RedisUser  # noqa: E402

USER_NAME = "pytest@user.com"
USER_HASH = '$2y$10$RbhyZ3xQYYoOgDaFJTl.seMWCEm18QDn.a6o9Cqw4K.3Bm4UzEFQS'
USER_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))


def test_redis_user_new():
    """
    Creating a new RedisUser
    """
    User = RedisUser().new(username=USER_NAME, hash=USER_HASH)

    assert User.name == USER_NAME
    assert User.hash == USER_HASH
    assert User.id == USER_ID


def test_redis_user_get_ok():
    """
    Querying a RedisUser
    """
    User = RedisUser(username=USER_NAME)

    assert User.name == USER_NAME
    assert User.hash == USER_HASH
    assert User.id == USER_ID


def test_redis_user_search_ok():
    """
    Searching a RedisUser
    """
    field_id = USER_ID.replace('-', ' ')
    Users = RedisSearch().user(query=f'@id:{field_id}')

    assert hasattr(Users, 'results') is True
    assert len(Users.results) == 1

    User = Users.results[0]
    assert User.name == USER_NAME
    assert User.hash == USER_HASH
    assert User.id == USER_ID

    User = Users.results_as_dict[0]
    assert User['name'] == USER_NAME
    assert User['hash'] == USER_HASH
    assert User['id'] == USER_ID


def test_redis_user_setters():
    """
    Querying a RedisUser, and modifiy attributes
    """
    # 1. From a direct Query
    User = RedisUser(username=USER_NAME)

    User.hash = 'plipplop'
    User.d_name = 'User#1234'

    # Lets check by calling again a Creature if it was updated in Redis
    UserAgain = RedisUser(username=USER_NAME)

    assert UserAgain.hash == 'plipplop'
    assert UserAgain.d_name == 'User#1234'

    # 1. From a Search Query
    field_id = USER_ID.replace('-', ' ')
    Users = RedisSearch().user(query=f'@id:{field_id}')

    assert hasattr(Users, 'results') is True
    assert len(Users.results) == 1
    Users.results[0].hash = 'plopplip'
    Users.results[0].d_name = 'User#4321'

    # Lets check by calling again a Creature if it was updated in Redis
    UserAgain = RedisUser(username=USER_NAME)

    assert UserAgain.hash == 'plopplip'
    assert UserAgain.d_name == 'User#4321'


def test_redis_user_to_json():
    """
    Querying a RedisUser, and dumping it as JSON
    """
    User = RedisUser(username=USER_NAME)

    assert json.loads(User.to_json())
    assert json.loads(User.to_json())['name'] == USER_NAME


def test_redis_user_del():
    """
    Removing a RedisUser
    """
    ret = RedisUser(username=USER_NAME).destroy()

    assert ret is True


def test_redis_user_del_ko():
    """
    Removing a RedisUser
    > Expected to fail
    """
    ret = RedisUser().destroy()

    assert ret is False


def test_redis_user_get_ko():
    """
    Querying a RedisUser
    > Expected to fail
    """
    User = RedisUser(username=USER_NAME)

    assert User.hkey == 'users'
    assert hasattr(User, 'id') is False
    assert hasattr(User, 'name') is False

    User = RedisUser()

    assert User.hkey == 'users'
    assert User.id is None
    assert User.name is None


def test_redis_user_search_empty():
    """
    Searching a RedisUser
    > Expected to fail
    """
    field_id = USER_ID.replace('-', ' ')
    Users = RedisSearch().user(query=f'@id:{field_id}')

    assert hasattr(Users, 'results') is True
    assert len(Users.results) == 0
