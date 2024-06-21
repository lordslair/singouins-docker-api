# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.User import UserDocument, UserDiscord  # noqa: E402

USER_NAME = 'user@exemple.net'
USER_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))
USER_HASH = 'PYTEST_HASH_PLACEHOLDER'


def test_mongodb_user_new():
    """
    Creating a new UserDocument
    """

    newUser = UserDocument(
        _id=uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME),
        discord=UserDiscord(),
        hash=USER_HASH,
        name=USER_NAME,
    )
    newUser.save()

    assert str(newUser.id) == USER_ID
    assert newUser.discord.ack is False
    assert newUser.hash == USER_HASH
    assert newUser.name == USER_NAME


def test_mongodb_user_get():
    """
    Querying a UserDocument
    """
    pass


def test_mongodb_user_search():
    """
    Searching a User
    """
    assert UserDocument.objects(_id=USER_ID).count() == 1
    assert UserDocument.objects(name=USER_NAME).count() == 1

    User = UserDocument.objects(_id=USER_ID).first()
    assert str(User.id) == USER_ID
