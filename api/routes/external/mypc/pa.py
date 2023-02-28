# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisPa       import RedisPa

from utils.routehelper          import (
    creature_check,
    )


#
# Routes /mypc/<uuid:creatureuuid>/pa/*
#
# API: GET /mypc/<uuid:creatureuuid>/pa
@jwt_required()
def pa_get(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Pa = RedisPa(creatureuuid=creatureuuid)
    except Exception as e:
        msg = f'{h} PA Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} PA Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Pa.as_dict(),
            }
        ), 200
