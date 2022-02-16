# -*- coding: utf8 -*-

import re

from .connector import r
from .metas     import get_meta

redpaduration  = 3600
bluepaduration = 3600

# Get the Meta stored in REDIS
try:
    metaSkills = get_meta('skill')
except Exception as e:
    print(f'[Redis:get_meta()] meta fetching failed [{e}]')

#
# Queries: cds:*
#

def add_cd(creature,duration,skillmetaid):
    # Pre-flight checks
    try:
        skill = metaSkills[skillmetaid - 1]
    except Exception as e:
        print(f'[Redis] skill not found (skillmetaid:{skillmetaid})')
        return False

    ttl       = duration * redpaduration
    mypattern = f"cds:{creature.instance}:{creature.id}:{skill['id']}"

    try:
        r.set(f'{mypattern}:duration_base',ttl,        ttl)
        r.set(f'{mypattern}:source'       ,creature.id,ttl)
    except Exception as e:
        print(f'[Redis] add_cd({mypattern}) failed [{e}]')
        return False
    else:
        return True

def get_cd(creature,skillmetaid):
    mypattern = f'cds:{creature.instance}:{creature.id}:{skillmetaid}'

    if r.get(f'{mypattern}:source') is None:
        return False

    try:
        cd = {"bearer":        creature.id,
              "duration_base": int(r.get(f'{mypattern}:duration_base')),
              "duration_left": int(r.ttl(f'{mypattern}:duration_base')),
              "id":            skillmetaid,
              "name":          metaSkills[skillmetaid - 1]['name'],
              "source":        int(r.get(f'{mypattern}:source')),
              "type":          'cd'}
    except Exception as e:
        print(f'[Redis] get_cd({mypattern}) failed [{e}]')
        return None
    else:
        if cd:
            return cd

def get_cds(creature):
    mypattern = f'cds:{creature.instance}:{creature.id}'
    cds       = []

    try:
        path = f'{mypattern}:*:source'
        #                    └────> Wildcard for {skillmetaid}
        keys = r.scan_iter(path)
    except Exception as e:
        print(f'[Redis] scan_iter({path}) failed [{e}]')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+)", key)
            #                            └────> Regex for {skillmetaid}
            if m:
                skillmetaid = int(m.group(1))
                skill       = metaSkills[skillmetaid - 1]
                fullkey     = f'{mypattern}:{skillmetaid}'
                cd          = {"bearer":        creature.id,
                               "duration_base": int(r.get(f'{fullkey}:duration_base')),
                               "duration_left": int(r.ttl(f'{fullkey}:duration_base')),
                               "id":            skillmetaid,
                               "name":          skill['name'],
                               "source":        int(r.get(f'{fullkey}:source')),
                               "type":          'cd'}
            cds.append(cd)
    except Exception as e:
        print(f'[Redis:get_cds()] Query {path} failed [{e}]')
        return cds
    else:
        return cds

def get_instance_cds(creature):
    mypattern = f'cds:{creature.instance}'
    path      = f'{mypattern}:*:*'
    #                         │ └────────> Wildcard for {creatureid}
    #                         └──────────> Wildcard for {skillmetaid}
    cds       = []

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

        # We loop over the cds keys to build the data
        for key in sorted_keys_source:
            m = re.match(f"{mypattern}:(\d+):(\d+)", key)
            #                            │     └────────> Regex for {skillmetaid}
            #                            └──────────────> Regex for {creatureid}
            if m:
                skillmetaid  = int(m.group(2))
                skillmeta    = metaSkills[skillmetaid - 1]
                cd           = {"bearer":        creature.id,
                                "duration_base": int(multi[index_multi]),
                                "duration_left": int(pipeline[index_pipeline]),
                                "id":            skillmeta['id'],
                                "name":          skillmeta['name'],
                                "source":        int(multi[index_multi+1]),
                                "type":          'cd'}
                # We update the index for next iteration
                index_multi    += 2
                index_pipeline += 1
                # We add the cd into cds list
                cds.append(cd)
    except Exception as e:
        print(f'[Redis:get_instance_cds()] Query {path} failed [{e}]')
        return cds
    else:
        return cds

def del_cd(creature,skillmetaid):
    count     = 0
    mypattern = f'cds:{creature.instance}:{creature.id}:{skillmetaid}:*'

    try:
        for key in r.scan_iter(mypattern):
            r.delete(key)
            count += 1
    except Exception as e:
        print(f'[Redis] del_cd({mypattern}) failed [{e}]')
        return False
    else:
        return count
