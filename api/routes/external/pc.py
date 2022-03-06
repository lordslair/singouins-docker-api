# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_inventory import *
from mysql.methods.fn_user      import fn_user_get

from nosql                      import *

#
# Routes /pc
#
# API: GET /pc/{pcid}
@jwt_required()
def pc_get_one(creatureid):
    (code, success, msg, payload) = fn_creature_get(None,creatureid)
    if isinstance(code, int):
        return jsonify({"success": success,
                        "msg": msg,
                        "payload": payload}), code

# API: GET /pc/{pcid}/item
@jwt_required()
def pc_item_get_all(creatureid):
    creature = fn_creature_get(None,creatureid)[3]

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200

    if creature.account is None:
        return jsonify({"success": False,
                        "msg": f'NPC Creature do not have items (creatureid:{creature.id})',
                        "payload": None}), 200

    try:
        equipment = fn_slots_get_all(creature)

        feet      = fn_item_get_one(equipment[0].feet)
        hands     = fn_item_get_one(equipment[0].hands)
        head      = fn_item_get_one(equipment[0].head)
        holster   = fn_item_get_one(equipment[0].holster)
        lefthand  = fn_item_get_one(equipment[0].lefthand)
        righthand = fn_item_get_one(equipment[0].righthand)
        shoulders = fn_item_get_one(equipment[0].shoulders)
        torso     = fn_item_get_one(equipment[0].torso)
        legs      = fn_item_get_one(equipment[0].legs)

        # We publicly anounce the cosmetics owned by a PC
        cosmetic  = fn_cosmetics_get_all(creature)
    except Exception as e:
        msg = f'[SQL] Equipment Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        feetmetaid      = feet.metaid      if feet      is not None else None
        handsmetaid     = hands.metaid     if hands     is not None else None
        headmetaid      = head.metaid      if head      is not None else None
        holstermetaid   = holster.metaid   if holster   is not None else None
        shouldersmetaid = shoulders.metaid if shoulders is not None else None
        torsometaid     = torso.metaid     if torso     is not None else None
        legsmetaid      = legs.metaid      if legs      is not None else None

        if righthand is not None and lefthand is not None:
            # PC has 2 weapons equipped.
            if righthand.id == lefthand.id:
                # PC has ONE two-handed weapon equipped. I send only meta inside RH
                righthandmetaid = righthand.metaid
                lefthandmetaid  = None
            else:
                # PC has TWO different weapons equipped.
                righthandmetaid = righthand.metaid
                lefthandmetaid  = lefthand.metaid
        else:
            # PC has 1 or 0 weapons equipped.
            righthandmetaid = righthand.metaid if righthand is not None else None
            lefthandmetaid  = lefthand.metaid  if lefthand  is not None else None

        feetmetatype      = feet.metatype      if feet      is not None else None
        handsmetatype     = hands.metatype     if hands     is not None else None
        headmetatype      = head.metatype      if head      is not None else None
        holstermetatype   = holster.metatype   if holster   is not None else None
        lefthandmetatype  = lefthand.metatype  if lefthand  is not None else None
        righthandmetatype = righthand.metatype if righthand is not None else None
        shouldersmetatype = shoulders.metatype if shoulders is not None else None
        torsometatype     = torso.metatype     if torso     is not None else None
        legsmetatype      = legs.metatype      if legs      is not None else None

        metas = {"feet": {"metaid": feetmetaid,"metatype": feetmetatype},
                "hands": {"metaid": handsmetaid,"metatype": handsmetatype},
                "head": {"metaid": headmetaid,"metatype": headmetatype},
                "holster": {"metaid": holstermetaid,"metatype": holstermetatype},
                "lefthand": {"metaid": lefthandmetaid,"metatype": lefthandmetatype},
                "righthand": {"metaid": righthandmetaid,"metatype": righthandmetatype},
                "shoulders": {"metaid": shouldersmetaid,"metatype": shouldersmetatype},
                "torso": {"metaid": torsometaid,"metatype": torsometatype},
                "legs": {"metaid": legsmetaid,"metatype": legsmetatype}}

        return jsonify({"success": True,
                        "msg": f'Equipment Query OK (creatureid:{creature.id})',
                        "payload": {"equipment": metas,
                                    "cosmetic": cosmetic}}), 200

# API: GET /pc/{pcid}/event
@jwt_required()
def pc_event_get_all(creatureid):
    creature = fn_creature_get(None,creatureid)[3]

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200

    try:
        creature_events = events.get_events(creature)
    except Exception as e:
        msg = f'Event Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Event Query OK (creatureid:{creature.id})',
                        "payload": creature_events}), 200
