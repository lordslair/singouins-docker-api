# -*- coding: utf8 -*-

import json

from .connector import r

#
# Queries: system:meta:*
#

def get_meta(metatype):
    mypattern = 'system:meta'

    try:
        if r.exists(f'{mypattern}:{metatype}'):
            meta = json.loads(r.get(f'{mypattern}:{metatype}').decode("utf-8"))
        else:
            return False
    except Exception as e:
        print(f'[Redis:get_meta()] Query failed [{e}]')
        return None
    else:
        return meta
