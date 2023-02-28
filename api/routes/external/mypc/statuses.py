# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch

from utils.routehelper          import (
    creature_check,
    )


#
# Routes /mypc/<uuid:creatureuuid>/statuses
#
# API: GET /mypc/<uuid:creatureuuid>/statuses
@jwt_required()
def statuses_get(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Statuses = RedisSearch().status(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} Statuses Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Statuses Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "statuses": [
                        Status.as_dict() for Status in Statuses.results
                        ],
                    "creature": Creature.as_dict(),
                    },
            }
        ), 200
