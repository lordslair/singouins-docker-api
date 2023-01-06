# -*- coding: utf8 -*-

import time

from datetime                   import datetime
from loguru                     import logger

from nosql.connector            import r


class RedisEvent:
    def __init__(self, creature):
        self.creature = creature
        self.logh     = f'[Creature.id:{self.creature.id}]'
        self.hkey     = f'events:{self.creature.id}'
        logger.trace(f'{self.logh} Method >> Initialization')

    def get(self):
        path      = f'{self.hkey}:*'
        #                         └────> Wildcard for {ts}
        events    = []

        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            # We get the list of keys for all the events
            keys               = r.keys(path)
            sorted_keys        = sorted(keys)
            # We loop over the events keys to build the data
            for key in sorted_keys:
                hashdict = r.hgetall(key)
                # We need to convert empty strings into None for Redis
                if hashdict['src'] == '':
                    src = None
                else:
                    src = hashdict['src']
                if hashdict['dst'] == '':
                    dst = None
                else:
                    dst = hashdict['dst']
                # We build the event item
                event = {
                    "src": src,
                    "action": hashdict['action'],
                    "date":
                        datetime.fromtimestamp(int(hashdict['ts']) // 1000),
                    "dst": dst,
                    "id": sorted_keys.index(key) + 1,
                    "type": hashdict['type'],
                }
                # We add the event into events list
                events.append(event)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return events

    def add(self, src, dst, type, action, ttl=None):
        ts  = time.time_ns() // 1000000  # Time in milliseconds

        try:
            logger.trace(f'{self.logh} Method >> (HASH Creating)')
            # We need to convert None into empty strings for Redis
            if src is None:
                src = ''
            if dst is None:
                dst = ''
            hashdict = {
                "action": action,
                "dst": dst,
                "src": src,
                "ts": ts,
                "type": type,
            }
            if ttl is None:
                r.hset(f'{self.hkey}:{ts}', mapping=hashdict)
            else:
                r.hset(f'{self.hkey}:{ts}', mapping=hashdict)
                r.expire(f'{self.hkey}:{ts}', ttl)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self):
        try:
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            r.delete(self.hkey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True
