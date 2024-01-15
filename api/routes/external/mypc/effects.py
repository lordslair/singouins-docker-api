# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisSearch   import RedisSearch

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/effects
#
# API: GET /mypc/<uuid:creatureuuid>/effects
@jwt_required()
# Custom decorators
@check_creature_exists
def effects_get(creatureuuid):
    try:
        Effects = RedisSearch().effect(
            query=f"@bearer:{g.Creature.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Effects Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Effects Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "effects": [
                        Effect.as_dict() for Effect in Effects.results
                        ],
                    "creature": g.Creature.as_dict(),
                    },
            }
        ), 200
