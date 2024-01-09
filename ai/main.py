#!/usr/bin/env python3
# -*- coding: utf8 -*-

import json
import os

from loguru                     import logger

from bestiaire.Salamander       import Salamander
from bestiaire.Fungus           import Fungus

from nosql.connector            import r_no_decode, redis
from nosql.models.RedisSearch   import RedisSearch

from utils.requests   import (
    resolver_generic_request_get,
    RESOLVER_URL,
    )

# Log System imports
logger.info('[core] System imports OK')

# Pre-flight check for Resolver connection
if os.environ.get("CI"):
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
    pubsub = r_no_decode.pubsub()
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
        Creatures = RedisSearch().creature(query='-(@instance:None)').results
    except Exception as e:
        logger.error(f"[Initialization] Creatures Query KO [{e}]")
    else:
        logger.trace("[Initialization] Creatures Query OK")

    if len(Creatures) > 0:
        logger.trace("Creature Loading >>")
        for Creature in Creatures:
            if Creature.race > 10:
                # Like a lazy ass, we publish it into the channel
                # to be treated in the listen() code
                try:
                    pmsg = {
                        "action": 'pop',
                        "creature": Creature.as_dict(),
                        }
                    r_no_decode.publish('ai-creature', json.dumps(pmsg))

                    name = f"[{Creature.id}] {Creature.name}"
                except Exception as e:
                    logger.error(f"Creature publish KO | {name} [{e}]")
                else:
                    logger.trace(f"Creature publish OK | {name}")
        logger.debug("Creature Loading OK")
    else:
        logger.debug("Creature Loading skipped (no Creatures fetched)")

    # We receive the events from Redis
    for msg in pubsub.listen():
        # We expect something like this as message
        """
        {
          "channel": <ai-{creature|instance}>,
          "data": {
            "action": <pop|kill>,
            "creature": <RedisCreature>
            },
          "pattern": <ai-{creature|instance}>,
          "type": "pmessage",
        }
        """

        channel = msg['channel'].decode('utf-8')
        if channel == 'ai-creature' and isinstance(msg['data'], bytes):
            try:
                data = json.loads(msg['data'])
            except Exception as e:
                logger.warning(f"Unable to parse data ({msg['data']}) [{e}]")
                continue
            else:
                pass

            if data['action'] == 'pop':
                # We have to pop a new creature somewhere
                name = f"[{data['creature']['id']}] {data['creature']['name']}"
                # We check that it exists in Redis
                Creatures = RedisSearch().creature(
                    query=f"@id:{data['creature']['id'].replace('-', ' ')}"
                    )
                if len(Creatures.results) != 1:
                    logger.warning(
                        f'Creature pop KO | {name} (NotFound in Redis)'
                        )
                else:
                    Creature = Creatures.results[0]
                    try:
                        if Creature.race in [11, 12, 13, 14]:
                            # Need to pop a Salamander
                            t = Salamander(creatureuuid=Creature.id)
                        elif Creature.race in [15, 16]:
                            # Need to pop a Fungus
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
            elif data['action'] == 'kill':
                # We have to kill an existing creature somewhere
                creature = data['creature']
                try:
                    killed = False
                    name = f"[{creature['id']}] {creature['name']}"
                    for index, thread in enumerate(threads_bestiaire):
                        if thread.creature.id == creature['id']:
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
                        logger.warning(
                            f"Creature kill KO | {name} (NotFound in threads)"
                            )
            elif data['action'] == 'update':
                # Some shit happened to a Creature - need to update thread info
                pass
            else:
                logger.warning(f"Action unknown (action:{data['action']})")

            # Every msg received we print bestiaire count
            logger.success(
                f'========== Status ({len(threads_bestiaire)}) =========='
                )
            if len(threads_bestiaire) > 0:
                for index, thread in enumerate(threads_bestiaire):
                    logger.success(
                        f"[{thread.creature.id}] {thread.creature.name} : "
                        f"{thread.stats.hp}/{thread.stats.hpmax} "
                        f"@({thread.creature.x},{thread.creature.y})"
                        )
                logger.success('============================')
