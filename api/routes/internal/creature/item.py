# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    request_json_check,
    )

from variables                  import YQ_DISCORD

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/item
def creature_item_add(creatureid):
    request_internal_token_check(request)
    request_json_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    item_caracs = {
        "metatype": request.json.get('metatype'),
        "metaid": request.json.get('metaid'),
        "bound": True,
        "bound_type": 'BoP',
        "modded": False,
        "mods": None,
        "state": 100,
        "rarity": request.json.get('rarity'),
    }

    try:
        Item = RedisItem(Creature).new(item_caracs)
    except Exception as e:
        msg = f'{h} Item Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": {
                    "item": Item._asdict(),
                    "winner": Creature._asdict(),
                    },
                "embed": True,
                "scope": f'Squad-{Creature.squad}',
                }
            )

        msg = f'{h} Item Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "item": Item._asdict(),
                    "creature": Creature._asdict(),
                    },
            }
        ), 201


# API: DELETE /internal/creature/{creatureid}/item/{itemid}
def creature_item_del(creatureid, itemid):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    try:
        Item = RedisItem(Creature).get(itemid)
        RedisItem(Creature).destroy(itemid)
    except Exception as e:
        msg = f'{h} Item Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Item Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "item": Item._asdict(),
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
