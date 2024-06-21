# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Resource import ResourceDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

RESOURCE = {
    "material": "Copper",
    "rarity": "Common",
    "sprite": "1.png",
    "visible": False,
    "x": 10,
    "y": 10,
}
RESOURCE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, RESOURCE['material']))
INSTANCE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, RESOURCE['material']))


def test_mongodb_resource_new():
    """
    Creating a new ResourceDocument
    """

    newResource = ResourceDocument(
        _id=RESOURCE_ID,
        instance=INSTANCE_ID,
        material=RESOURCE['material'],
        rarity=RESOURCE['rarity'],
        sprite=RESOURCE['sprite'],
        visible=RESOURCE['visible'],
        x=RESOURCE['x'],
        y=RESOURCE['y'],
    )
    newResource.save()

    assert str(newResource.id) == RESOURCE_ID
    assert str(newResource.instance) == INSTANCE_ID
    assert newResource.rarity == RESOURCE['rarity']


def test_mongodb_resource_get():
    """
    Querying a ResourceDocument
    """
    pass


def test_mongodb_resource_search():
    """
    Searching a ResourceDocument
    """
    assert ResourceDocument.objects(_id=RESOURCE_ID).count() == 1

    Resource = ResourceDocument.objects(_id=RESOURCE_ID).get()
    assert str(Resource.id) == RESOURCE_ID
    assert str(Resource.instance) == INSTANCE_ID
    assert Resource.rarity == RESOURCE['rarity']


def test_mongodb_resource_del():
    """
    Removing a ResourceDocument
    """

    Resources = ResourceDocument.objects(_id=RESOURCE_ID)
    if Resources.count() > 0:
        for Resource in Resources:
            Resource.delete()

    assert ResourceDocument.objects(_id=RESOURCE_ID).count() == 0
