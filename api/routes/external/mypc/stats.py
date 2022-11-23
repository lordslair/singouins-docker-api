# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{pcid}/stats/*
#


# API: GET /mypc/{pcid}/stats
@jwt_required()
def stats_get(pcid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    try:
        Stats = RedisStats(Creature)
    except Exception as e:
        msg = f'{h} Stats Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'{h} Stats Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Stats._asdict(),
            }
        ), 200
