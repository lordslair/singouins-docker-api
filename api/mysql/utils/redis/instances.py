# -*- coding: utf8 -*-

from .connector import r

#
# Queries: instances:*
#

def get_instance(instanceid):
    mypattern = f'instances:{instanceid}'

    try:
        instance = {"creator":  int(r.get(f'{mypattern}:creator').decode("utf-8")),
                    "fast":     bool(r.get(f'{mypattern}:fast').decode("utf-8")),
                    "hardcore": bool(r.get(f'{mypattern}:hardcore').decode("utf-8")),
                    "id":       instanceid,
                    "map":      int(r.get(f'{mypattern}:map').decode("utf-8")),
                    "public":   bool(r.get(f'{mypattern}:public').decode("utf-8")),
                    "tick":     int(r.get(f'{mypattern}:tick').decode("utf-8"))}
    except Exception as e:
        print(f'[Redis] get_instance({mypattern}) failed [{e}]')
        return False
    else:
        return instance

def add_instance(creature,fast,hardcore,mapid,public):
    if fast == True:
        tick = 5
    else:
        tick = 3600

    # Need to find the latest instance id
    keys           = list(r.scan_iter('instances:*:creator'))
    if len(keys) == 0:
        # If this instance is the first created
        lastinstanceid = 0
    else:
        lastkey        = sorted(keys)[-1].decode("utf-8")
        lastinstanceid = int(lastkey.split(":")[1])

    mypattern      = f'instances:{lastinstanceid + 1}'

    try:
        r.set(f'{mypattern}:creator',  creature.id)
        r.set(f'{mypattern}:fast',     str(fast))
        r.set(f'{mypattern}:hardcore', str(hardcore))
        r.set(f'{mypattern}:map',      mapid)
        r.set(f'{mypattern}:public',   str(public))
        r.set(f'{mypattern}:tick',     tick)
    except Exception as e:
        print(f'[Redis] add_instance() failed [{e}]')
        return False
    else:
        return get_instance(lastinstanceid + 1)

def del_instance(instanceid):
    count     = 0
    mypattern = f'instances:{instanceid}:*'

    try:
        for key in r.scan_iter(mypattern):
            r.delete(key)
            count += 1
    except Exception as e:
        print(f'[Redis] del_instance({mypattern}) failed [{e}]')
        return False
    else:
        return count
