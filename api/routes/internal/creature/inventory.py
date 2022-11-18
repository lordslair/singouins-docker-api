# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/inventory
def creature_inventory_get(creatureid):
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
        bearer = Creature.id.replace('-', ' ')
        Inventory = RedisItem(Creature).search(field='bearer', query=bearer)
    except Exception as e:
        msg = f'{h} Inventory Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Inventory Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "inventory": Inventory,
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
