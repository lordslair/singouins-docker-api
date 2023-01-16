# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

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
    User = RedisUser().get(username=USER_NAME)

    assert User.name == USER_NAME
    assert User.hash == USER_HASH
    assert User.id == USER_ID


def test_redis_user_search_ok():
    """
    Searching a RedisUser
    """
    Users = RedisUser().search(field='id', query=USER_ID.replace('-', ' '))

    assert Users[0]['name'] == USER_NAME
    assert Users[0]['hash'] == USER_HASH
    assert Users[0]['id'] == USER_ID


def test_redis_user_del():
    """
    Removing a RedisUser
    """
    ret = RedisUser().destroy(username=USER_NAME)

    assert ret is True


def test_redis_user_get_ko():
    """
    Querying a RedisUser
    > Expected to fail
    """
    User = RedisUser().get(username=USER_NAME)

    assert User is False


def test_redis_user_search_empty():
    """
    Searching a RedisUser
    > Expected to fail
    """
    Users = RedisUser().search(field='id', query=USER_ID.replace('-', ' '))

    assert len(Users) == 0
