# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisUser     import RedisUser


#
# Routes /mypc/{pcid}/stats/*
#
# API: GET /mypc/{pcid}/stats
@jwt_required()
def stats_get(pcid):
    Creature = RedisCreature().get(pcid)
    User = RedisUser().get(get_jwt_identity())

    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging
    if Creature.account != User.id:
        msg = (f'{h} Token/username mismatch (username:{User.name})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

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
