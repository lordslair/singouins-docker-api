# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisStats    import RedisStats


#
# Routes /mypc/{pcid}/stats/*
#
# API: GET /mypc/{pcid}/stats
@jwt_required()
def stats_get(pcid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (pcid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        # We check if we have the data in redis
        creature_stats  = RedisStats(creature)
    except Exception as e:
        msg = f'Stats Query KO (creature.id:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'Stats Query OK (creature.id:{creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": creature_stats.dict,
            }
        ), 200
