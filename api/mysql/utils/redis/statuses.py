# -*- coding: utf8 -*-

import re
import time

from .connector import r
from .metas     import get_meta

redpaduration  = 3600
bluepaduration = 3600

# Get the Meta stored in REDIS
try:
    metaStatuses = get_meta('status')
except Exception as e:
    print(f'[Redis:get_meta()] meta fetching failed [{e}]')

#
# Queries: statuses:*
#

def add_status(creature,duration,statusmetaid):
    # Pre-flight checks
    try:
        statusmeta = dict(list(filter(lambda x:x["id"]==statusmetaid,metaStatuses))[0])
    except Exception as e:
        print(f'[Redis] Status not found (statusmetaid:{statusmetaid}) [{e}]')
        return False

    ttl       = duration * redpaduration
    mypattern = f"statuses:{creature.instance}:{creature.id}:{statusmeta['id']}"

    try:
        r.set(f'{mypattern}:duration_base',ttl,        ttl)
        r.set(f'{mypattern}:source'       ,creature.id,ttl)
    except Exception as e:
        print(f'[Redis] add_status({mypattern}) failed [{e}]')
        return False
    else:
        return True

def get_status(creature,statusmetaid):
    mypattern = f'statuses:{creature.instance}:{creature.id}:{statusmetaid}'

    if r.get(f'{mypattern}:source') is None:
        return False

    try:
        statusmeta = dict(list(filter(lambda x:x["id"]==statusmetaid,metaStatuses))[0])
        status = {"bearer":        creature.id,
                  "duration_base": int(r.get(f'{mypattern}:duration_base')),
                  "duration_left": int(r.ttl(f'{mypattern}:duration_base')),
                  "id":            statusmeta['id'],
                  "name":          statusmeta['name'],
                  "source":        int(r.get(f'{mypattern}:source')),
                  "type":          'status'}
    except Exception as e:
        print(f'[Redis] get_status({mypattern}) failed [{e}]')
        return None
    else:
        if status:
            return status

def get_statuses(creature):
    mypattern = f'statuses:{creature.instance}:{creature.id}'
    statuses  = []

    try:
        path = f'{mypattern}:*:source'
        #                    └────> Wildcard for {statusmetaid}
        keys = r.scan_iter(path)
    except Exception as e:
        print(f'[Redis] scan_iter({path}) failed [{e}]')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+)", key)
            if m:
                statusmetaid = int(m.group(1))
                statusmeta   = dict(list(filter(lambda x:x["id"]==statusmetaid,metaStatuses))[0])
                fullkey      = mypattern + ':' + f'{statusmetaid}'
                status       = {"bearer":          creature.id,
                                "duration_base":   int(r.get(f'{fullkey}:duration_base')),
                                "duration_left":   int(r.ttl(f'{fullkey}:duration_base')),
                                "id":              statusmeta['id'],
                                "name":            statusmeta['name'],
                                "source":          int(r.get(f'{fullkey}:source')),
                                "type":            'status'}
                statuses.append(status)
    except Exception as e:
        print(f'[Redis] get_statuses({path}) failed [{e}]')
        return statuses
    else:
        return statuses

def get_instance_statuses(creature):
    mypattern = f'statuses:{creature.instance}'
    path      = f'{mypattern}:*:*'
    #                         │ └────────> Wildcard for {creatureid}
    #                         └──────────> Wildcard for {statusmetaid}
    statuses  = []

    try:
        # We get the list of keys for all the instance statuses
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
            m = re.match(f"{mypattern}:(\d+):(\d+)", key)
            #                            │     └────────> Regex for {statusmetaid}
            #                            └──────────────> Regex for {creatureid}
            if m:
                statusmetaid = int(m.group(2))
                statusmeta   = dict(list(filter(lambda x:x["id"]==statusmetaid,metaStatuses))[0])
                status       = {"bearer":        creature.id,
                                "duration_base": int(multi[index_multi]),
                                "duration_left": int(pipeline[index_pipeline]),
                                "id":            statusmeta['id'],
                                "name":          statusmeta['name'],
                                "source":        int(multi[index_multi+1]),
                                "type":          'status'}
                # We update the index for next iteration
                index_multi    += 2
                index_pipeline += 1
                # We add the status into statuses list
                statuses.append(status)
    except Exception as e:
        print(f'[Redis:get_instance_statuses()] Query {path} failed [{e}]')
        return statuses
    else:
        return statuses

def del_status(creature,statusmetaid):
    count     = 0
    mypattern = f'statuses:{creature.instance}:{creature.id}:{statusmetaid}:*'

    try:
        for key in r.scan_iter(mypattern):
            r.delete(key)
            count += 1
    except Exception as e:
        print(f'[Redis] del_status({mypattern}) failed [{e}]')
        return False
    else:
        return count
