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
# Routes /mypc/<uuid:creatureuuid>/cds
#
# API: GET /mypc/<uuid:creatureuuid>/cds
@jwt_required()
def cds_get(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Cds = RedisSearch().cd(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} Cds Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Cds Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "cds": [
                        Cd.as_dict() for Cd in Cds.results
                        ],
                    "creature": Creature.as_dict(),
                    },
            }
        ), 200
