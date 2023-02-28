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
# Routes /mypc/<uuid:creatureuuid>/effects
#
# API: GET /mypc/<uuid:creatureuuid>/effects
@jwt_required()
def effects_get(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Effects = RedisSearch().effect(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} Effects Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Effects Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "effects": [
                        Effect.as_dict() for Effect in Effects.results
                        ],
                    "creature": Creature.as_dict(),
                    },
            }
        ), 200
