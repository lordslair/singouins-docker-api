# -*- coding: utf8 -*-

import time

from datetime import datetime

from nosql.connector            import *

class RedisEvent:
    def __init__(self,creature):
        RedisEvent.creature = creature
        RedisEvent.logh     = f'[creature.id:{RedisEvent.creature.id}]'

    @classmethod
    def get(cls):
        mypattern = f'events:{RedisEvent.creature.id}'
        path      = f'{mypattern}:*'
        #                         └────> Wildcard for {ts}
        events    = []

        try:
            # We get the list of keys for all the events
            keys               = r.keys(path)
            sorted_keys        = sorted(keys)
            # We MULTI the query to have all the values
            multi              = r.mget(sorted_keys)
            # We initialize indexes used during iterations
            index_multi        = 0
            # We loop over the events keys to build the data
            for key in sorted_keys:
                m = re.match(f'events:(\d+|None):(\d+):(\d+|None):(\w+)', key)
                #                         │       │        │       └────> Regex for {type}
                #                         │       │        └────────────> Regex for {dst}
                #                         │       └─────────────────────> Regex for {ts}
                #                         └─────────────────────────────> Regex for {src}
                if m:
                    # None (string) to Pythonic None conversion
                    if m.group(1) == 'None':
                        src = None
                    else:
                        src = int(m.group(1))
                    if m.group(3) == 'None':
                        dst = None
                    else:
                        dst = int(m.group(3))
                    # We build the event item
                    event = {"src":           src,
                             "action":        multi[index_multi],
                             "date":          datetime.fromtimestamp(int(m.group(2))//1000),
                             "dst":           dst,
                             "id":            index_multi+1,
                             "type":          m.group(4)}
                    # We update the index for next iteration
                    index_multi    += 1
                    # We add the event into events list
                    events.append(event)
        except Exception as e:
            logger.error(f'{RedisEvent.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{RedisEvent.logh} Method OK')
            return events


    @classmethod
    def add(cls,src,dst,type,msg,ttl=None):

        ts  = time.time_ns() // 1000000 # Time in milliseconds
        key = f'events:{src}:{ts}:{dst}:{type}'

        try:
            if ttl is None:
                r.set(key, msg)
            else:
                r.set(key, msg, ttl)
        except Exception as e:
            logger.error(f'{RedisEvent.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{RedisEvent.logh} Method OK')
            return True
