# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Korp import KorpDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

KORP_NAME = 'PyTest Korp'
KORP_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, KORP_NAME))


def test_mongodb_korp_new():
    """
    Creating a new KorpDocument
    """

    newKorp = KorpDocument(
        _id=KORP_ID,
        leader=CREATURE_ID,
        name=KORP_NAME,
        )
    newKorp.save()

    assert str(newKorp.id) == KORP_ID
    assert str(newKorp.leader) == CREATURE_ID
    assert newKorp.name == KORP_NAME


def test_mongodb_korp_get():
    """
    Querying a KorpDocument
    """
    pass


def test_mongodb_korp_search():
    """
    Searching a KorpDocument
    """
    assert KorpDocument.objects(leader=CREATURE_ID).count() == 1

    Korp = KorpDocument.objects(leader=CREATURE_ID).get()
    assert str(Korp.leader) == CREATURE_ID
    assert Korp.name == KORP_NAME


def test_mongodb_korp_del():
    """
    Removing a KorpDocument
    """

    Korps = KorpDocument.objects(leader=CREATURE_ID)
    if Korps.count() > 0:
        for Korp in Korps:
            Korp.delete()

    assert KorpDocument.objects(leader=CREATURE_ID).count() == 0
