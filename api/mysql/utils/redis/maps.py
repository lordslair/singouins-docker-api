# -*- coding: utf8 -*-

import json

from .connector import r

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
        map = {"data": json.loads(r.get(f'{mypattern}:data').decode("utf-8")),
               "id":   mapid,
               "mode": r.get(f'{mypattern}:mode').decode("utf-8"),
               "size": r.get(f'{mypattern}:size').decode("utf-8"),
               "type": r.get(f'{mypattern}:type').decode("utf-8")}
    except Exception as e:
        print(f'[Redis] get_map({mypattern}) failed [{e}]')
        return False
    else:
        return map
