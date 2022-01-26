# -*- coding: utf8 -*-

import json
import re
import time

from .connector import r

redpaduration  = 3600
bluepaduration = 3600

# Get the Meta stored in REDIS
try:
    metaEffects = json.loads(r.get('system:meta:effects'))
except Exception as e:
    print(f'[Redis] metaEffects fetching failed [{e}]')

#
# Queries: effects:*
#

def add_effect(creature,duration,effectmetaid,source):
    # Pre-flight checks
    try:
        effect = metaEffects[effectmetaid - 1]
    except Exception as e:
        print(f'[Redis] effect not found (effectmetaid:{effectmetaid})')
        return False

    ttl       = duration * redpaduration
    effectid  = time.time_ns() // 1000000 # Time in milliseconds
    mypattern = f"effects:{creature.instance}:{creature.id}:{effect['id']}:{effectid}"

    try:
        r.set(f'{mypattern}:duration_base',duration)
        r.set(f'{mypattern}:source',source.id)
    except Exception as e:
        print(f'[Redis] add_effect({mypattern}) failed [{e}]')
        return False
    else:
        return True

def get_effect(creature,effectid):
    count     = 0
    mypattern = f'effects:{creature.instance}:{creature.id}'

    try:
        path = f'{mypattern}:*:{effectid}:source'
        #                    └────> Wildcard for {effectmetaid}
        keys = r.scan_iter(path)
    except Exception as e:
        print(f'[Redis] scan_iter({path}) failed [{e}]')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+):(\d+)", key.decode("utf-8"))
            #                            │     └────> Regex for {effectid}
            #                            └──────────> Regex for {effectmetaid}
            if m:
                count       += 1
                effectmetaid = int(m.group(1))
                fullkey      = f'{mypattern}:{effectmetaid}:{effectid}'
                effect       = {"bearer":          creature.id,
                                "duration_base":   int(r.get(f'{fullkey}:duration_base').decode("utf-8")),
                                "duration_left":   int(r.get(f'{fullkey}:duration_base').decode("utf-8")),
                                "id":              effectid,
                                "name":            metaEffects[effectmetaid - 1]['name'],
                                "source":          r.get(f'{fullkey}:source').decode("utf-8"),
                                "type":            'effect'}
    except Exception as e:
        print(f'[Redis] get_effect({path}) failed [{e}]')
        return None
    else:
        if count == 0:
            return False
        else:
            return effect

def get_effects(creature):
    mypattern = f'effects:{creature.instance}:{creature.id}'
    effects   = []

    try:
        path = f'{mypattern}:*:*:source'
        #                    │ └──> Wildcard for {effectid}
        #                    └────> Wildcard for {effectmetaid}
        keys = r.scan_iter(path)
    except Exception as e:
        print(f'[Redis] scan_iter({path}) failed [{e}]')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+):(\d+)", key.decode("utf-8"))
            #                            │     └────> Regex for {effectid}
            #                            └──────────> Regex for {effectmetaid}
            if m:
                effectmetaid = int(m.group(1))
                effectid     = int(m.group(2))
                fullkey      = f'{mypattern}:{effectmetaid}:{effectid}'
                effect       = {"bearer":          creature.id,
                                "duration_base":   int(r.get(f'{fullkey}:duration_base').decode("utf-8")),
                                "duration_left":   int(r.get(f'{fullkey}:duration_base').decode("utf-8")),
                                "id":              effectid,
                                "name":            metaEffects[effectmetaid - 1]['name'],
                                "source":          r.get(f'{fullkey}:source').decode("utf-8"),
                                "type":            'effect'}
                effects.append(effect)
    except Exception as e:
        print(f'[Redis] get_effects({path}) failed [{e}]')
        return effects
    else:
        return effects

def del_effect(creature,effectid):
    count     = 0
    mypattern = f'effects:{creature.instance}:{creature.id}:*:{effectid}:*'
    #                                                       └─> effectmetaid

    try:
        for key in r.scan_iter(mypattern):
            r.delete(key)
            count += 1
    except Exception as e:
        print(f'[Redis] del_effect({mypattern}) failed [{e}]')
        return False
    else:
        return count
