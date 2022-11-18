# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/position/{x}/{y}
def creature_position_set(creatureid, x, y):
    Creature = RedisCreature().get(creatureid)
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

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

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
