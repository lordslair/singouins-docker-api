# -*- coding: utf8 -*-

import re
import time

from .connector import r
from .metas     import get_meta

redpaduration  = 3600
bluepaduration = 3600

# Get the Meta stored in REDIS
try:
    metaEffects = get_meta('effect')
except Exception as e:
    print(f'[Redis:get_meta()] meta fetching failed [{e}]')

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
            m = re.match(f"{mypattern}:(\d+):(\d+)", key)
            #                            │     └────> Regex for {effectid}
            #                            └──────────> Regex for {effectmetaid}
            if m:
                count       += 1
                effectmetaid = int(m.group(1))
                fullkey      = f'{mypattern}:{effectmetaid}:{effectid}'
                effect       = {"bearer":          creature.id,
                                "duration_base":   int(r.get(f'{fullkey}:duration_base')),
                                "duration_left":   int(r.get(f'{fullkey}:duration_base')),
                                "id":              effectid,
                                "name":            metaEffects[effectmetaid - 1]['name'],
                                "source":          r.get(f'{fullkey}:source'),
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
            m = re.match(f"{mypattern}:(\d+):(\d+)", key)
            #                            │     └────> Regex for {effectid}
            #                            └──────────> Regex for {effectmetaid}
            if m:
                effectmetaid = int(m.group(1))
                effectid     = int(m.group(2))
                fullkey      = f'{mypattern}:{effectmetaid}:{effectid}'
                effect       = {"bearer":          creature.id,
                                "duration_base":   int(r.get(f'{fullkey}:duration_base')),
                                "duration_left":   int(r.get(f'{fullkey}:duration_base')),
                                "id":              effectid,
                                "name":            metaEffects[effectmetaid - 1]['name'],
                                "source":          r.get(f'{fullkey}:source'),
                                "type":            'effect'}
                effects.append(effect)
    except Exception as e:
        print(f'[Redis] get_effects({path}) failed [{e}]')
        return effects
    else:
        return effects

def get_instance_effects(creature):
    mypattern = f'effects:{creature.instance}'
    path      = f'{mypattern}:*:*:*:source'
    #                         │ │ └──> Wildcard for {effectid}
    #                         │ └────> Wildcard for {effectmetaid}
    #                         └──────> Wildcard for {creatureid}
    effects   = []

    try:
        for key in r.scan_iter(path):
            m = re.match(f"{mypattern}:(\d+):(\d+):(\d+)", key)
            #                            │     │     └────> Regex for {effectid}
            #                            │     └──────────> Regex for {effectmetaid}
            #                            └────────────────> Regex for {creatureid}
            if m:
                creatureid   = int(m.group(1))
                effectmetaid = int(m.group(2))
                effectid     = int(m.group(3))
                fullkey      = f'{mypattern}:{creatureid}:{effectmetaid}:{effectid}'
                effect       = {"bearer":          creatureid,
                                "duration_base":   int(r.get(f'{fullkey}:duration_base')),
                                "duration_left":   int(r.get(f'{fullkey}:duration_base')),
                                "id":              effectid,
                                "name":            metaEffects[effectmetaid - 1]['name'],
                                "source":          r.get(f'{fullkey}:source'),
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
