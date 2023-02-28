# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.maps                 import get_map


#
# Routes /map
#
# API: GET /map/<int:mapid>
@jwt_required()
def map_get(mapid):
    # Pre-flight checks
    if not isinstance(mapid, int):
        return jsonify({"success": False,
                        "msg": f'Map ID should be an integer (mapid:{mapid})',
                        "payload": None}), 200
    try:
        map = get_map(mapid)
    except Exception as e:
        msg = f'Map query KO (mapid:{mapid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if map:
            msg = f'Map query OK (mapid:{mapid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": map,
                }
            ), 200
        else:
            msg = f'Map query KO - Not Found (mapid:{mapid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
