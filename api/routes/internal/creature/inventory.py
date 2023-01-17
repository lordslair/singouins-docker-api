# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/inventory
def creature_inventory_get(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=creatureid)
    h = creature_check(Creature)

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
                    "creature": Creature.as_dict(),
                    },
            }
        ), 200
