# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_inventory import (fn_item_get_one,
                                        fn_item_ammo_set)

from nosql.models.RedisSlots    import RedisSlots

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/equipment
def creature_equipment(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        creature_slots = RedisSlots(creature)
    except Exception as e:
        msg = f'{h} Slots Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        equipment = {
            "feet":      fn_item_get_one(creature_slots.feet),
            "hands":     fn_item_get_one(creature_slots.hands),
            "head":      fn_item_get_one(creature_slots.head),
            "holster":   fn_item_get_one(creature_slots.holster),
            "lefthand":  fn_item_get_one(creature_slots.lefthand),
            "righthand": fn_item_get_one(creature_slots.righthand),
            "shoulders": fn_item_get_one(creature_slots.shoulders),
            "torso":     fn_item_get_one(creature_slots.torso),
            "legs":      fn_item_get_one(creature_slots.legs),
            }
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
    else:
        msg = f'{h} Equipment Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "equipment": equipment,
                    "creature": creature,
                    },
            }
        ), 200


# API: GET /internal/creature/{creatureid}/equipment/{itemid}/ammo/{operation}/{count} # noqa
def creature_equipment_modifiy(creatureid, itemid, operation, count):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    if operation not in ['add', 'consume']:
        msg = (f"Operation should be in "
               f"['add','consume'] (operation:{operation})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        item = fn_item_get_one(itemid)
        if item and item.ammo > 0:
            if operation == 'consume':
                item_modified = fn_item_ammo_set(item.id, item.ammo - count)
            else:
                item_modified = fn_item_ammo_set(item.id, item.ammo + count)
        else:
            msg = f'{h} Item Query KO (itemid:{itemid})'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
    except Exception as e:
        msg = f'{h} Item Query KO (itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if item_modified:
            msg = f'{h} Item Query OK (itemid:{itemid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "item": item_modified,
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Item Query KO (itemid:{itemid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
