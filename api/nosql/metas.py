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


# Loading the Meta for later use
metaArmors = get_meta('armor')
metaRaces = get_meta('race')
metaWeapons = get_meta('weapon')

if __name__ == '__main__':

    for meta in metaArmors:
        for k, v in meta.items():
            if v is None:
                meta[k] = 'None'
            elif v is False:
                meta[k] = 'False'
            elif v is True:
                meta[k] = 'True'
        r.hset(f"metas:armor:{meta['id']}", mapping=meta)
    for meta in metaRaces:
        for k, v in meta.items():
            if v is None:
                meta[k] = 'None'
            elif v is False:
                meta[k] = 'False'
            elif v is True:
                meta[k] = 'True'
        r.hset(f"metas:race:{meta['id']}", mapping=meta)
    for meta in metaWeapons:
        for k, v in meta.items():
            if v is None:
                meta[k] = 'None'
            elif v is False:
                meta[k] = 'False'
            elif v is True:
                meta[k] = 'True'
        r.hset(f"metas:weapon:{meta['id']}", mapping=meta)
