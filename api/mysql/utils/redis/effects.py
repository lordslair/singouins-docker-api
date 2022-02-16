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
        r.set(f'{mypattern}:duration_base',ttl,        ttl)
        r.set(f'{mypattern}:source'       ,source.id,  ttl)
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
                                "source":          int(r.get(f'{fullkey}:source')),
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
        print(f'[Redis:get_effects()] Query {path} failed [{e}]')
        return effects
    else:
        return effects

def get_instance_effects(creature):
    mypattern = f'effects:{creature.instance}'
    path      = f'{mypattern}:*:*:*'
    #                         │ │ └──> Wildcard for {effectid}
    #                         │ └────> Wildcard for {effectmetaid}
    #                         └──────> Wildcard for {creatureid}
    effects   = []

    try:
        # We get the list of keys for all the instance effects
        keys               = r.keys(path)
        sorted_keys        = sorted(keys)
        # We MULTI the query to have all the values
        multi              = r.mget(sorted_keys)
        # We initialize indexes used during iterations
        index_multi        = 0
        index_pipeline     = 0
        # We regex to have only the :source keys
        regex              = re.compile(".*source")
        sorted_keys_source = list(filter(regex.match, sorted_keys))
        # We create a pipeline to query the keys TTL
        p = r.pipeline()
        for key in sorted_keys_source:
            p.ttl(key)
        pipeline = p.execute()

        # We loop over the effect keys to build the data
        for key in sorted_keys_source:
            m = re.match(f"{mypattern}:(\d+):(\d+):(\d+)", key)
            #                            │     │     └────> Regex for {effectid}
            #                            │     └──────────> Regex for {effectmetaid}
            #                            └────────────────> Regex for {creatureid}
            if m:
                effectmetaid = int(m.group(2))
                effectid     = int(m.group(3))
                effectmeta   = dict(list(filter(lambda x:x["id"]==effectmetaid,metaEffects))[0])
                effect       = {"bearer":          creature.id,
                                "duration_base":   int(multi[index_multi]),
                                "duration_left":   int(pipeline[index_pipeline]),
                                "id":              effectid,
                                "name":            effectmeta['name'],
                                "source":          int(multi[index_multi+1]),
                                "type":            'effect'}

                # We update the index for next iteration
                index_multi += 2
                index_pipeline += 1
                # We add the effect into effects list
                effects.append(effect)
    except Exception as e:
        print(f'[Redis:get_instance_effects()] Query {path} failed [{e}]')
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
