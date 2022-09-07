# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r

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
        logger.error(f'Meta Query KO [{e}]')
        return None
    else:
        logger.trace('Meta Query OK')
        return meta
