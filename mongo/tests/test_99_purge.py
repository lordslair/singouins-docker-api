# -*- coding: utf8 -*-

import os
import sys
import uuid

from mongoengine import Q

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Creature import CreatureDocument  # noqa: E402
from mongo.models.Item import ItemDocument  # noqa: E402
from mongo.models.User import UserDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

USER_NAME = 'user@exemple.net'
USER_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, USER_NAME))
USER_HASH = 'PYTEST_HASH_PLACEHOLDER'


#
#
#
def test_mongodb_item_del_ok():
    """
    Removing a ItemDocument
    """

    query = Q(bearer=CREATURE_ID)
    Items = ItemDocument.objects(query)
    if len(Items) > 0:
        for Item in Items:
            Item.delete()

    assert ItemDocument.objects(bearer=CREATURE_ID).count() == 0


def test_mongodb_item_del_ko():
    """
    Removing a ItemDocument
    > Expected to fail
    """

    assert ItemDocument.objects(bearer='plop').delete() == 0


def test_mongodb_item_search_empty():
    """
    Searching a ItemDocument
    > Expected to fail
    """

    assert ItemDocument.objects(bearer='plop').count() == 0


#
# Delete CREATURE
#
def test_mongodb_creature_del_ok():
    """
    Removing a CreatureDocument
    """

    query = Q(_id=CREATURE_ID)
    Creatures = CreatureDocument.objects(query)
    if len(Creatures) > 0:
        for Creature in Creatures:
            Creature.delete()

    assert CreatureDocument.objects(_id=CREATURE_ID).count() == 0


def test_mongodb_creature_del_ko():
    """
    Removing a CreatureDocument
    > Expected to fail
    """

    assert CreatureDocument.objects(name='plop').delete() == 0


def test_mongodb_creature_search_empty():
    """
    Searching a CreatureDocument
    > Expected to fail
    """

    assert CreatureDocument.objects(name='plop').count() == 0


#
# DELETE USER
#
def test_mongodb_user_del_ok():
    """
    Removing a UserDocument
    """

    query = Q(_id=USER_ID)
    Users = UserDocument.objects(query)
    if len(Users) > 0:
        for User in Users:
            User.delete()

    assert UserDocument.objects(_id=USER_ID).count() == 0


def test_mongodb_user_del_ko():
    """
    Removing a UserDocument
    > Expected to fail
    """

    assert UserDocument.objects(name='plop').delete() == 0


def test_mongodb_user_search_empty():
    """
    Searching a UserDocument
    > Expected to fail
    """

    assert UserDocument.objects(name='plop').count() == 0
