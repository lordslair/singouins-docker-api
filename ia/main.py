#!/usr/bin/env python3
# -*- coding: utf8 -*-

import json
import os

from loguru                     import logger
from redis                      import Redis

from bestiaire.Salamander       import Salamander
from bestiaire.Fungus           import Fungus

from bestiaire.utils.requests   import (
    api_internal_generic_request_get,
    resolver_generic_request_get,
    )

# Log System imports
logger.info('[DB:*][core] [✓] System imports')

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB      = os.environ['SEP_REDIS_DB']

# API variables
API_INTERNAL_HOST  = os.environ['SEP_BACKEND_API_INTERNAL_SVC_SERVICE_HOST']
API_INTERNAL_PORT  = os.environ['SEP_BACKEND_API_INTERNAL_SVC_SERVICE_PORT']
API_INTERNAL_URL   = f'http://{API_INTERNAL_HOST}:{API_INTERNAL_PORT}'
API_INTERNAL_TOKEN = os.environ['SEP_INTERNAL_TOKEN']

# Resolver variables
RESOLVER_HOST = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_HOST")
RESOLVER_PORT = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_PORT")
RESOLVER_URL  = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'

# Pre-flight check for API connection
try:
    ret = api_internal_generic_request_get(
        path="/up"
    )
except Exception as e:
    logger.error(f'API connection KO ({API_INTERNAL_URL}) [{e}]')
    exit()
else:
    if ret['success'] is True:
        logger.info(f'API connection OK ({API_INTERNAL_URL})')
    else:
        logger.warning(f'API connection KO ({API_INTERNAL_URL})')
        exit()

# Pre-flight check for Resolver connection
try:
    ret = resolver_generic_request_get(
        path="/check"
    )
except Exception as e:
    logger.error(f'Resolver connection KO ({RESOLVER_URL}) [{e}]')
    exit()
else:
    if ret['success'] is True:
        logger.info(f'Resolver connection OK ({RESOLVER_URL})')
    else:
        logger.warning(f'Resolver connection KO ({RESOLVER_URL})')
        exit()

# Subscriber pattern
SUB_PATHS = ['ai-instance', 'ai-creature']

# Opening Redis connection
try:
    r = Redis(host=REDIS_HOST,
              port=REDIS_PORT,
              db=REDIS_DB,
              socket_connect_timeout=1)
    pubsub = r.pubsub()
except (Redis.ConnectionError,
        Redis.BusyLoadingError):
    logger.error(f'[DB:{REDIS_DB}][core] [✗] Connection to Redis')
else:
    logger.info(f'[DB:{REDIS_DB}][core] [✓] Connection to Redis')

# Starting subscription
for path in SUB_PATHS:
    try:
        pubsub.psubscribe(path)
    except Exception as e:
        logger.error(f'[DB:{REDIS_DB}][core] [✗] Sub to Redis:"{path}" [{e}]')
    else:
        logger.info(f'[DB:{REDIS_DB}][core] [✓] Sub to Redis:"{path}"')

if __name__ == '__main__':
    # We initialise counters
    threads_bestiaire = []
    try:
        # We Initialize with ALL the existing NPC Creatures in an instance
        ret = api_internal_generic_request_get(
            path="/creatures"
        )
    except Exception as e:
        logger.error(
            f"[Initialization] Creatures Query KO [{e}]"
            )
    else:
        logger.trace(
            "[Initialization] Creatures Query OK"
            )
        creatures = ret['payload']

    if len(creatures):
        for creature in creatures:
            if creature['race'] > 10:
                # Like a lazy ass, we publish it into the channel
                # to be treated in the listen() code
                try:
                    # First we fetch the Creature stats
                    ret = api_internal_generic_request_get(
                        path=f"/creature/{creature['id']}/stats"
                    )
                    stats = ret['payload']['stats']
                except Exception as e:
                    logger.error(
                        f"[Creature.id:{creature['id']}] Stats Query KO [{e}]"
                        )
                else:
                    logger.trace(
                        f"[Creature.id:{creature['id']}] Stats Query OK"
                        )

                try:
                    pmsg = {
                        "action": 'pop',
                        "instance": None,
                        "creature": creature,
                        "stats": stats,
                        }
                    pchannel = 'ai-creature'
                    name = f"[{creature['id']}] {creature['name']}"
                    r.publish(pchannel, json.dumps(pmsg))
                except Exception as e:
                    logger.error(f"Creature publish KO | {name} [{e}]")
                else:
                    logger.trace(f"Creature publish OK | {name}")

    # We receive the events from Redis
    for msg in pubsub.listen():
        # We expect something like this inside data['creature']
        """
        {
          "channel":"ai-XXX",
          "data": {},
          "pattern":"ai-XXX",
          "type": "pmessage",
        }
        """

        channel = msg['channel'].decode('utf-8')
        if channel == 'ai-creature' and isinstance(msg['data'], bytes):
            try:
                data    = json.loads(msg['data'])
            except Exception as e:
                logger.warning(f"Unable to parse data ({msg['data']}) [{e}]")
                continue
            else:
                pass

            """
            "data":{
              "action":"pop",
              "creature":{},
              "instance": None,
              "stats":{
                "base":{
                  "b":50,
                  "g":50,
                  "m":50,
                  "p":100,
                  "r":50,
                  "v":0
                },
                "def":{
                  "armor":{
                    "b":0,
                    "p":0
                  },
                  "dodge":50,
                  "hp":150,
                  "hpmax":150,
                  "parry":1
                },
                "off":{
                  "capcom":50,
                  "capsho":25
                }
              }
            }
            """

            if data['action'] == 'pop':
                # We have to pop a new creature somewhere
                creature = data['creature']

                """
                "creature":{
                  "account": None,
                  "created":"2022-12-05 15:38:18",
                  "date":"2022-12-05 15:38:18",
                  "gender":true,
                  "id":"dcfe3118-8bd6-4ceb-b392-80bc09b0b35f",
                  "instance":"f128cf79-c9c3-4fe3-a227-29b960aa4cbf",
                  "korp": None,
                  "korp_rank": None,
                  "level":1,
                  "name":"Fungus Toxicus",
                  "race":16,
                  "rarity":"Unique",
                  "squad": None,
                  "squad_rank": None,
                  "targeted_by": None,
                  "x":4,
                  "xp":0,
                  "y":4
                }
                """

                try:
                    name = f"[{creature['id']}] {creature['name']}"
                    if any([
                        creature['race'] == 11,
                        creature['race'] == 12,
                        creature['race'] == 13,
                        creature['race'] == 14,
                    ]):
                        # Need to pop a Salamander
                        t = Salamander(creature, stats)
                    elif any([
                        creature['race'] == 15,
                        creature['race'] == 16,
                    ]):
                        # Need to pop a Fungus
                        t = Fungus(creature, stats)
                    else:
                        # Gruik
                        pass

                    t.start()
                    threads_bestiaire.append(t)
                except Exception as e:
                    logger.error(f"Creature pop KO | {name} [{e}]")
                else:
                    logger.debug(f"Creature pop OK | {name}")
            elif data['action'] == 'kill':
                # We have to kill an existing creature somewhere
                creature = data['creature']
                try:
                    name = f"[{creature['id']}] {creature['name']}"
                    for index, thread in enumerate(threads_bestiaire):
                        if thread.id == creature['id']:
                            # We got the dead Creature
                            logger.trace(f'Creature to kill found: {name}')
                            thread.hp = 0
                            threads_bestiaire.remove(thread)

                except Exception as e:
                    logger.error(f"Creature kill KO | {name} [{e}]")
                else:
                    logger.debug(f"Creature kill OK | {name}")
            elif data['action'] == 'update':
                # Some shit happened to a Creature - need to update thread info
                pass
            else:
                logger.warning(f"Action unknown (action:{data['action']})")

            # Every msg received we print bestiaire count
            logger.success(f'========== '
                           f'Status ({len(threads_bestiaire)}) '
                           f'==========')
            if len(threads_bestiaire) > 0:
                for index, thread in enumerate(threads_bestiaire):
                    logger.success(f"[{thread.id}] {thread.name} : "
                                   f"{thread.hp}/{thread.hp_max} "
                                   f"@({thread.x},{thread.y})")
                logger.success('============================')
