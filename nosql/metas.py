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
metaRecipes = get_meta('recipe')
metaWeapons = get_meta('weapon')
metaConsumables = get_meta('consumable')

# META varlables
"""
This is a HUGE Dictionary to manipulate pore easiliy all the metas
Without having to query Redis all the time internally
"""

metaNames = {
    "weapon": {
        },
    "armor": {
        },
    "race": {
        },
}
for meta in metaWeapons:
    metaNames['weapon'][meta['id']] = meta
for meta in metaArmors:
    metaNames['armor'][meta['id']] = meta
for meta in metaRaces:
    metaNames['race'][meta['id']] = meta
