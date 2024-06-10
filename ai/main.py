#!/usr/bin/env python3
# -*- coding: utf8 -*-

import json
import os

from loguru import logger
from mongoengine import Q

from bestiaire import (
    Salamander,
    Fungus
    )

from mongo.models.Creature import CreatureDocument

from nosql.connector import r, redis

from utils.requests import (
    resolver_generic_request_get,
    RESOLVER_URL,
    RESOLVER_CHECK_SKIP,
    )

# Log System imports
logger.info('[core] System imports OK')

# Pre-flight check for Resolver connection
if os.environ.get("CI"):
    pass
elif RESOLVER_CHECK_SKIP:
    pass
else:
    try:
        ret = resolver_generic_request_get(
            path="/check"
        )
    except Exception as e:
        logger.error(f'[core] >> Resolver KO ({RESOLVER_URL}) [{e}]')
        exit()
    else:
        if ret and ret['success'] is True:
            logger.info(f'[core] >> Resolver OK ({RESOLVER_URL})')
        else:
            logger.warning(f'[core] >> Resolver KO ({RESOLVER_URL})')

# Subscriber pattern
SUB_PATHS = ['ai-instance', 'ai-creature']

# Opening Redis connection
try:
    pubsub = r.pubsub()
except (redis.Redis.ConnectionError,
        redis.Redis.BusyLoadingError) as e:
    logger.error(f'[core] >> Redis KO [{e}]')
else:
    logger.info('[core] >> Redis OK')

# Starting subscription
for path in SUB_PATHS:
    try:
        pubsub.psubscribe(path)
    except Exception as e:
        logger.error(f'[core] Subscribe to Redis:"{path}" KO [{e}]')
    else:
        logger.info(f'[core] Subscribe to Redis:"{path}" OK')

if __name__ == '__main__':
    # We initialise counters
    threads_bestiaire = []
    try:
        # We Initialize with ALL the existing NPC Creatures in an instance
        query = (Q(instance__exists=True) & Q(race__gt=10))
        Creatures = CreatureDocument.objects(query)
    except CreatureDocument.DoesNotExist:
        logger.debug("[Initialization] Skipped (no Creatures fetched)")
    except Exception as e:
        logger.error(f"[Initialization] Creatures Query KO [{e}]")
    else:
        logger.trace("[Initialization] Creatures Query OK")
        logger.trace("Creature Loading >>")
        for Creature in Creatures:
            # Like a lazy ass, we publish it into the channel
            # to be treated in the listen() code
            try:
                pmsg = {
                    "action": 'pop',
                    "creature": Creature.to_json(),
                    }
                r.publish('ai-creature', json.dumps(pmsg))
            except Exception as e:
                logger.error(f"Creature publish KO | [{Creature.id}] {Creature.name} [{e}]")
            else:
                logger.trace(f"Creature publish OK | [{Creature.id}] {Creature.name}")
        logger.debug("Creature Loading OK")

    # We receive the events from Redis
    for msg in pubsub.listen():
        # We expect something like this as message
        """
        {
          "channel": <ai-{creature|instance}>,
          "data": {
            "action": <pop|kill>,
            "creature": <CreatureDocument.to_json()>
            },
          "pattern": <ai-{creature|instance}>,
          "type": "pmessage",
        }
        """

        if msg['channel'] in ['ai-creature'] and msg['type'] == 'pmessage':
            try:
                data = json.loads(msg['data'])
            except Exception as e:
                logger.warning(f"Unable to json.loads ({msg['data']}) [{e}]")
                continue
            else:
                pass
        else:
            continue

        if msg['channel'] == 'ai-creature' and data['action'] == 'pop':
            # We have to pop a new creature somewhere
            creature = json.loads(data['creature'])
            logger.trace(f'pmessage["data"]: {creature}')
            name = f"[{creature['_id']}] {creature['name']}"
            # We check that it exists in MongoDB
            try:
                Creature = CreatureDocument.objects(_id=creature['_id']).get()
            except CreatureDocument.DoesNotExist:
                logger.warning(f'Creature pop KO | {name} (NotFound in MongoDB)')
            else:
                try:
                    if Creature.race in [11, 12, 13, 14]:
                        # Need to pop a Salamander
                        logger.trace('We pop a Salamander')
                        t = Salamander(creatureuuid=Creature.id)
                    elif Creature.race in [15, 16]:
                        # Need to pop a Fungus
                        logger.trace('We pop a Fungus')
                        t = Fungus(creatureuuid=Creature.id)
                    else:
                        # Gruik
                        pass
                        logger.warning(data)

                    t.start()
                    threads_bestiaire.append(t)
                except Exception as e:
                    logger.error(f'Creature pop KO | {name} [{e}]')
                else:
                    logger.debug(f'Creature pop OK | {name}')
        elif msg['channel'] == 'ai-creature' and data['action'] == 'kill':
            # We have to kill an existing creature somewhere
            creature = json.loads(data['creature'])
            try:
                killed = False
                name = f"[{creature['_id']}] {creature['name']}"
                for index, thread in enumerate(threads_bestiaire):
                    if thread.creature.id == creature['_id']:
                        # We got the dead Creature
                        logger.trace(f'Creature to kill found: {name}')
                        thread.creature.hp = 0
                        threads_bestiaire.remove(thread)
                        killed = True
            except Exception as e:
                logger.error(f"Creature kill KO | {name} [{e}]")
            else:
                if killed is True:
                    logger.debug(f"Creature kill OK | {name}")
                else:
                    logger.warning(f"Creature kill KO | {name} (NotFound in threads)")
        elif msg['channel'] == 'ai-creature' and data['action'] == 'update':
            # Some shit happened to a Creature - need to update thread info
            pass
        else:
            logger.warning(f"Message unknown (data:{data})")

        # Every msg received we print bestiaire count
        if len(threads_bestiaire) > 0:
            logger.success(f'========== Status BEGIN ({len(threads_bestiaire)})')
            for index, thread in enumerate(threads_bestiaire):
                logger.success(
                    f"[{thread.creature.id}] {thread.creature.name} : "
                    f"{thread.creature.hp.current}/{thread.creature.hp.max} "
                    f"@({thread.creature.x},{thread.creature.y})"
                    )
            logger.success('========== Status END')
