# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisItem     import RedisItem
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
        equipment = {}
        for slot in [
            'feet', 'hands', 'head',
            'holster', 'lefthand', 'righthand',
            'shoulders', 'torso', 'legs'
        ]:
            itemuuid = getattr(creature_slots, slot)
            if itemuuid is None:
                # If the Slot is empty, let's put None directly
                equipment[slot] = None
            else:
                # An item is equipped in this slot, lets gather info
                item = RedisItem(creature).get(itemuuid)
                if item:
                    equipment[slot] = item._asdict()
                else:
                    equipment[slot] = None
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
        item = RedisItem(creature).get(itemid)
        if item and item.ammo > 0:
            if operation == 'consume':
                item.ammo -= count
            else:
                item.ammo += count
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
        msg = f'{h} Item Query OK (itemid:{itemid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "item": item._asdict(),
                    "creature": creature,
                    },
            }
        ), 200
