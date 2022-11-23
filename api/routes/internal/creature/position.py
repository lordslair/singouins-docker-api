# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/position/{x}/{y}
def creature_position_set(creatureid, x, y):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    try:
        Creature.x = x
        Creature.y = y
    except Exception as e:
        msg = f'{h} Position Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Position Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature._asdict(),
            }
        ), 200
