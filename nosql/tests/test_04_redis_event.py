# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisEvent import RedisEvent  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_redis_event_new():
    """
    Creating a new RedisEvent
    """
    Event = RedisEvent().new(
        action_src=CREATURE_ID,
        action_dst=None,
        action_type='action/craft',
        action_text='Crafted something',
        action_ttl=30 * 86400,
        )

    assert Event.src == CREATURE_ID
    assert Event.dst is None
    assert Event.type == 'action/craft'


def test_redis_event_get_ok():
    """
    Querying a RedisEvent
    """
    Event = RedisEvent().new(
        action_src=CREATURE_ID,
        action_dst=None,
        action_type='action/craft',
        action_text='Crafted something',
        action_ttl=30 * 86400,
        )

    EventAgain = RedisEvent(eventuuid=Event.id)

    assert EventAgain.src == CREATURE_ID
    assert EventAgain.dst is None
    assert EventAgain.type == 'action/craft'


def test_redis_event_to_json():
    """
    Querying a RedisEvent, and dumping it as JSON
    """
    pass


def test_redis_cosmetic_search_ok():
    """
    Searching a Event
    """
    src = CREATURE_ID.replace('-', ' ')
    Events = RedisSearch().event(query=f'@src:{src}')

    Event = Events.results_as_dict[0]
    assert Event['src'] == CREATURE_ID

    Event = Events.results[0]
    assert Event.src == CREATURE_ID


def test_redis_event_del():
    """
    Removing a RedisEvent
    """
    src = CREATURE_ID.replace('-', ' ')
    Events = RedisSearch().cosmetic(query=f'(@src:{src}) & (@dst:None)')
    for Event in Events.results:
        ret = Event.destroy()
        assert ret is True


def test_redis_event_del_ko():
    """
    Removing a RedisEvent
    > Expected to fail
    """
    ret = RedisEvent().destroy()

    assert ret is False


def test_redis_event_get_ko():
    """
    Querying a RedisEvent
    > Expected to fail
    """
    Event = RedisEvent()

    assert Event.hkey == 'events'
    assert hasattr(Event, 'id') is False


def test_redis_event_search_empty():
    """
    Searching a RedisEvent
    > Expected to fail
    """
    Events = RedisSearch().event(query='@src:plop')

    assert len(Events.results) == 0
