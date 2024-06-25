# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisSearch   import RedisSearch

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/statuses
#
# API: GET /mypc/<uuid:creatureuuid>/statuses
@jwt_required()
# Custom decorators
@check_creature_exists
def statuses_get(creatureuuid):
    try:
        Statuses = RedisSearch().status(
            query=f"@bearer:{str(g.Creature.id).replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Statuses Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Statuses Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "statuses": [Status.as_dict() for Status in Statuses.results],
                    "creature": g.Creature.to_mongo(),
                    },
            }
        ), 200
