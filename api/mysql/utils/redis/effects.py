# -*- coding: utf8 -*-

import re
import time

from .connector import r

redpaduration  = 3600
bluepaduration = 3600

#
# Queries: effects:*
#

def add_effect(creature,duration,effectname,source):
    # Input checks
    if not isinstance(duration, int):
        print(f'add_effect() Bad duration format (duration:{duration})')
        return False
    if not isinstance(effectname, str):
        print(f'add_effect() Bad Effectname format (effectname:{effectname})')
        return False

    ttl       = duration * redpaduration
    ns        = time.time_ns()
    mypattern = f'effects:{creature.instance}:{creature.id}:{effectname}:{ns}'

    try:
        r.set(f'{mypattern}:bearer',creature.id)
        r.set(f'{mypattern}:duration_base',duration)
        r.set(f'{mypattern}:duration_left',duration)
        r.set(f'{mypattern}:source',source.id)
        r.set(f'{mypattern}:type','effect')
    except Exception as e:
        print(f'set_effect() failed [{e}]')
        return False
    else:
        return True

def get_effects(creature):
    mypattern = f'effects:{creature.instance}:{creature.id}'
    effects   = []

    try:
        keys = r.scan_iter(mypattern + ':*:*:bearer')
        #                                │ └──> Wildcard for {nanosec}
        #                                └────> Wildcard for {effectname}
    except Exception as e:
        print(f'scan_iter({mypattern}) failed [{e}]')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\w+):(\d+)", key.decode("utf-8"))
            if m:
                effectname = m.group(1)
                ns         = int(m.group(2))
                fullkey    = mypattern + f':{effectname}:{ns}'
                effect     = {"bearer":          int(r.get(fullkey + ':bearer').decode("utf-8")),
                              "duration_base":   int(r.get(fullkey + ':duration_base').decode("utf-8")),
                              "duration_left":   int(r.get(fullkey + ':duration_left').decode("utf-8")),
                              "id":              ns,
                              "source":          r.get(fullkey + ':source').decode("utf-8"),
                              "type":            r.get(fullkey + ':type').decode("utf-8"),
                              "name":            effectname}
                effects.append(effect)
            else:
                print('shit happened in regex')
    except Exception as e:
        print(f'Effects fetching failed:{e}')
        return effects
    else:
        return effects

def del_effect(effectid):
    # Input checks
    if not isinstance(effectid, int):
        print(f'del_effect() effectid format (effectid:{effectid})')
        return False

    count     = 0
    mypattern = f'effects:*:*:*:{effectid}:*'
    #                     │ │ └─> effectname
    #                     │ └───> creatureid
    #                     └─────> instanceid

    try:
        for key in r.scan_iter(mypattern):
            r.delete(key)
            count += 1
    except Exception as e:
        print(f'del_effect() failed [{e}]')
        return False
    else:
        return count
