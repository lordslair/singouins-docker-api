# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{pcid}/pa/*
#


# API: GET /mypc/{pcid}/pa
@jwt_required()
def pa_get(pcid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    try:
        creature_pa = RedisPa(Creature)._asdict()
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
                "payload": creature_pa,
            }
        ), 200
