# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Profession import ProfessionDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_mongodb_profession_new():
    """
    Creating a new ProfessionDocument
    """

    newProfession = ProfessionDocument(
        _id=CREATURE_ID,
    )
    newProfession.save()

    assert str(newProfession.id) == CREATURE_ID


def test_mongodb_profession_get():
    """
    Querying a ProfessionDocument
    """
    pass


def test_mongodb_profession_search():
    """
    Searching a ProfessionDocument
    """
    assert ProfessionDocument.objects(_id=CREATURE_ID).count() == 1

    Profession = ProfessionDocument.objects(_id=CREATURE_ID).get()
    assert str(Profession.id) == CREATURE_ID


def test_mongodb_profession_del():
    """
    Removing a ProfessionDocument
    """

    Professions = ProfessionDocument.objects(_id=CREATURE_ID)
    if Professions.count() > 0:
        for Profession in Professions:
            Profession.delete()

    assert ProfessionDocument.objects(_id=CREATURE_ID).count() == 0
