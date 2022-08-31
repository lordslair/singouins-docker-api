# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_inventory import (fn_slots_get_one,
                                        fn_item_get_one,
                                        fn_item_ammo_set)

from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: GET /internal/creature/{creatureid}/equipment
def creature_equipment(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    try:
        slots = fn_slots_get_one(creature)
    except Exception as e:
        msg = f'Slots Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        equipment = {"feet":      fn_item_get_one(slots.feet),
                     "hands":     fn_item_get_one(slots.hands),
                     "head":      fn_item_get_one(slots.head),
                     "holster":   fn_item_get_one(slots.holster),
                     "lefthand":  fn_item_get_one(slots.lefthand),
                     "righthand": fn_item_get_one(slots.righthand),
                     "shoulders": fn_item_get_one(slots.shoulders),
                     "torso":     fn_item_get_one(slots.torso),
                     "legs":      fn_item_get_one(slots.legs)}
    except Exception as e:
        msg = f'Equipment Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'Equipment Query OK (creatureid:{creature.id})'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": {"equipment": equipment,
                                    "creature": creature}}), 200

# API: GET /internal/creature/{creatureid}/equipment/{itemid}/ammo/{operation}/{count}
def creature_equipment_modifiy(creatureid,itemid,operation,count):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    if operation not in ['add','consume']:
        return jsonify({"success": False,
                        "msg":     f"Operation should be in ['add','consume'] (operation:{operation})",
                        "payload": None}), 200

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    try:
        item = fn_item_get_one(itemid)
        if item and item.ammo > 0:
            if operation == 'consume':
                item_modified = fn_item_ammo_set(item.id,item.ammo - count)
            else:
                item_modified = fn_item_ammo_set(item.id,item.ammo + count)
        else:
            msg = f'Item Query KO (creatureid:{creature.id},itemid:{itemid})'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
    except Exception as e:
        msg = f'Item Query KO (creatureid:{creature.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if item_modified:
            msg = f'Item Query OK (creatureid:{creature.id},itemid:{itemid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"item": item_modified,
                                        "creature": creature}}), 200
        else:
            msg = f'Item Query KO (creatureid:{creature.id},itemid:{itemid})'
            logger.debug(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
