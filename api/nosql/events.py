# -*- coding: utf8 -*-

import time
from datetime import datetime

from .connector import *

def set_event(src,dst,type,msg,ttl=None):
    ts  = time.time_ns() // 1000000 # Time in milliseconds
    key = f'events:{src}:{ts}:{dst}:{type}'

    try:
        if ttl is None:
            r.set(key, msg)
        else:
            r.set(key, msg, ttl)
    except Exception as e:
        logger.error(f'Query KO [{e}]')
        return False
    else:
        return True

def get_events(creature,count=50):
    mypattern = f'events:{creature.id}'
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
            m = re.match(f"{mypattern}:(\d+):(\d+|None):(\w+)", key)
            #                            │     │     └────> Regex for {type}
            #                            │     └──────────> Regex for {dst}
            #                            └────────────────> Regex for {ts}
            if m:
                if m.group(2) == 'None':
                    dst = None
                else:
                    dst = int(m.group(2))
                event = {"src":           creature.id,
                         "action":        multi[index_multi],
                         "date":          datetime.fromtimestamp(int(m.group(1))//1000),
                         "dst":           dst,
                         "id":            index_multi+1,
                         "type":          m.group(3)}
                # We update the index for next iteration
                index_multi    += 1
                # We add the event into events list
                events.append(event)
    except Exception as e:
        logger.error(f'Query KO [{e}]')
        return events
    else:
        return events
