# -*- coding: utf8 -*-

import os
import sys
import uuid

from mongoengine import Q

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Event import EventDocument  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

EVENT_DST = None
EVENT_NAME = 'action/profession/skinning'
EVENT_TYPE = 10


def test_mongodb_event_new():
    """
    Creating a new EventDocument
    """

    firstEvent = EventDocument(
        action='ACTION String',
        dst=EVENT_DST,
        extra=None,
        name=EVENT_NAME,
        src=CREATURE_ID,
        trigger=None,
        type=EVENT_TYPE,
        )
    firstEvent.save()

    assert str(firstEvent.src) == CREATURE_ID
    assert firstEvent.dst == EVENT_DST
    assert firstEvent.type == EVENT_TYPE
    assert firstEvent.name == EVENT_NAME


def test_mongodb_event_get():
    """
    Querying a EventDocument
    """
    pass


def test_mongodb_event_search():
    """
    Searching a Event
    """
    assert EventDocument.objects(src=CREATURE_ID).count() == 1
    assert EventDocument.objects(name=EVENT_NAME).count() == 1

    Event = EventDocument.objects(src=CREATURE_ID).first()
    assert str(Event.src) == CREATURE_ID


def test_mongodb_event_del():
    """
    Removing a EventDocument
    """

    query = Q(src=CREATURE_ID) | Q(dst=None)
    Events = EventDocument.objects(query)
    if len(Events) > 0:
        for Event in Events:
            Event.delete()

    assert EventDocument.objects(src=CREATURE_ID).count() == 0
