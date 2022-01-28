# -*- coding: utf8 -*-

from .connector import r

#
# Queries: system:maps:*
#

def get_map(mapid):
    mypattern = f'system:maps:{mapid}'

    try:
        map = r.get(f'{mypattern}').decode("utf-8")
    except Exception as e:
        print(f'[Redis] get_map({mypattern}) failed [{e}]')
        return False
    else:
        return map
