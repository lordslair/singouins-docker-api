# -*- coding: utf8 -*-

from ..utils.redis.maps      import get_map

#
# Queries /map/*
#

# API: GET /mypc/map/<int:mapid>
def mypc_map_get(mapid):
    # Pre-flight checks
    if not isinstance(mapid, int):
        return (200,
                False,
                f'Map ID should be an integer (mapid:{mapid})',
                None)

    try:
        map = get_map(mapid)
    except Exception as e:
        return (200,
                False,
                f'[Redis:get_map()] Map query failed (mapid:{mapid})',
                None)
    else:
        if map:
            return (200,
                    True,
                    f'[Redis:get_map()] Map query successed (mapid:{mapid})',
                    map)
        else:
            return (200,
                    True,
                    f'Map not found (mapid:{mapid})',
                    None)
