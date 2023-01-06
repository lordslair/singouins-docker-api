# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r

#
# Queries: system:maps:*
#


def get_map(mapid):
    mypattern = f'system:map:{mapid}'

    # We check that the map keys exists
    try:
        keys = r.exists(f'{mypattern}:data')
    except Exception as e:
        logger.error(f'Map Query KO [{e}]')
        return False
    else:
        if keys:
            pass
        else:
            logger.debug(f'Query returned empty for {mypattern}:data')
            return False

    try:
        map = {"data": json.loads(r.get(f'{mypattern}:data')),
               "id": mapid,
               "mode": r.get(f'{mypattern}:mode'),
               "size": r.get(f'{mypattern}:size'),
               "type": r.get(f'{mypattern}:type')}
    except Exception as e:
        logger.error(f'Map Query KO [{e}]')
        return False
    else:
        logger.trace('Map Query OK')
        return map
