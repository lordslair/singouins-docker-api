# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisSlots    import RedisSlots

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/equipment
def creature_equipment(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    try:
        Slots = RedisSlots(Creature)
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
            itemuuid = getattr(Slots, slot)
            if itemuuid is None:
                # If the Slot is empty, let's put None directly
                equipment[slot] = None
            else:
                # An item is equipped in this slot, lets gather info
                item = RedisItem(Creature).get(itemuuid)
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
                    "creature": Creature._asdict(),
                    },
            }
        ), 200


# API: GET /internal/creature/{creatureid}/equipment/{itemid}/ammo/{operation}/{count} # noqa
def creature_equipment_modifiy(creatureid, itemid, operation, count):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    if operation not in ['add', 'consume']:
        msg = (f"{h} Operation should be in "
               f"['add','consume'] (operation:{operation})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Item = RedisItem(Creature).get(itemid)
        if Item and Item.ammo > 0:
            if operation == 'consume':
                Item.ammo -= count
            else:
                Item.ammo += count
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
                    "item": Item._asdict(),
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
