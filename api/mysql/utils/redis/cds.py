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
        print(f'[Redis] get_cds({path}) failed [{e}]')
        return cds
    else:
        return cds

def get_instance_cds(creature):
    mypattern = f'cds:{creature.instance}'
    path      = f'{mypattern}:*:*:source'
    #                         │ └────────> Wildcard for {creatureid}
    #                         └──────────> Wildcard for {skillmetaid}
    cds       = []

    try:
        for key in r.scan_iter(path):
            m = re.match(f"{mypattern}:(\d+):(\d+)", key)
            #                            │     └────────> Regex for {skillmetaid}
            #                            └──────────────> Regex for {creatureid}
            if m:
                creatureid  = int(m.group(1))
                skillmetaid = int(m.group(2))
                skill       = metaSkills[skillmetaid - 1]
                fullkey     = f'{mypattern}:{creatureid}:{skillmetaid}'
                cd          = {"bearer":        creatureid,
                               "duration_base": int(r.get(f'{fullkey}:duration_base')),
                               "duration_left": int(r.ttl(f'{fullkey}:duration_base')),
                               "id":            skillmetaid,
                               "name":          skill['name'],
                               "source":        int(r.get(f'{fullkey}:source')),
                               "type":          'cd'}
            cds.append(cd)
    except Exception as e:
        print(f'[Redis] get_cds({path}) failed [{e}]')
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
