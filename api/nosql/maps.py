# -*- coding: utf8 -*-

from .connector import *

#
# Queries: system:maps:*
#

def get_map(mapid):
    mypattern = f'system:maps:{mapid}'

    # We check that the map keys exists
    try:
        keys = r.keys(f'{mypattern}:data')
    except Exception as e:
        print(f'[Redis] get_map({mypattern}) failed [{e}]')
        return False
    else:
        # The map does not exist
        if len(keys) == 0:
            return False

    try:
        map = {"data": json.loads(r.get(f'{mypattern}:data')),
               "id":   mapid,
               "mode": r.get(f'{mypattern}:mode'),
               "size": r.get(f'{mypattern}:size'),
               "type": r.get(f'{mypattern}:type')}
    except Exception as e:
        print(f'[Redis] get_map({mypattern}) failed [{e}]')
        return False
    else:
        return map
