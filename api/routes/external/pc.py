# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisCosmetic import RedisCosmetic
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisSlots    import RedisSlots

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /pc
#


# API: GET /pc/{pcid}
@jwt_required()
def pc_get_one(creatureid):
    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    msg = f'{h} Creature Query OK'
    logger.trace(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": Creature._asdict(),
        }
    ), 200


# API: GET /pc/{pcid}/item
@jwt_required()
def pc_item_get_all(creatureid):
    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    # Response skeleton
    metas = {
        "feet": {
            "metaid": None,
            "metatype": None,
        },
        "hands": {
            "metaid": None,
            "metatype": None
        },
        "head": {
            "metaid": None,
            "metatype": None
        },
        "holster": {
            "metaid": None,
            "metatype": None
        },
        "lefthand": {
            "metaid": None,
            "metatype": None
        },
        "righthand": {
            "metaid": None,
            "metatype": None
        },
        "shoulders": {
            "metaid": None,
            "metatype": None
        },
        "torso": {
            "metaid": None,
            "metatype": None
        },
        "legs": {
            "metaid": None,
            "metatype": None
        },
    }

    # Check to see if the request is for a Monster, and not a player.
    if Creature.account is None:
        msg = f'{h} Equipment Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "equipment": metas,
                    "cosmetic": [],
                    },
            }
        ), 200

    try:
        creature_slots = RedisSlots(Creature)

        # We publicly anounce the cosmetics owned by a PC
        creature_cosmetics = RedisCosmetic(Creature).get_all()
    except Exception as e:
        msg = f'{h} Equipment Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        for slot in [
            'feet',
            'hands',
            'head',
            'holster',
            'lefthand',
            'legs',
            'righthand',
            'shoulders',
            'torso',
        ]:
            itemuuid = getattr(creature_slots, slot)
            Item = RedisItem(Creature).get(itemuuid)

            if Item:
                metas[slot]['metaid'] = Item.metaid
                metas[slot]['metatype'] = Item.metatype

        # We need to clean some shit for 2H weapons
        # Ugly
        # Gruik
        if metas['lefthand']['metaid'] == metas['righthand']['metaid']:
            metas['lefthand']['metaid'] = None
            metas['lefthand']['metatype'] = None
    except Exception as e:
        msg = f'{h} Items Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    msg = f'{h} Equipment Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "equipment": metas,
                "cosmetic": creature_cosmetics,
                },
        }
    ), 200


# API: GET /pc/{pcid}/event
@jwt_required()
def pc_event_get_all(creatureid):
    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    try:
        creature_events = RedisEvent(Creature).get()
    except Exception as e:
        msg = f'{h} Event Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Event Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": creature_events,
            }
        ), 200
