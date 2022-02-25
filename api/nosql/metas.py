# -*- coding: utf8 -*-

from .connector import *

#
# Queries: system:meta:*
#

def get_meta(metatype):
    mypattern = 'system:meta'

    try:
        if r.exists(f'{mypattern}:{metatype}'):
            meta = json.loads(r.get(f'{mypattern}:{metatype}'))
        else:
            return False
    except Exception as e:
        print(f'[Redis:get_meta()] Query failed [{e}]')
        return None
    else:
        return meta
