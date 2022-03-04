# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import jwt_required

from mysql.methods      import fn_creature_get
from mysql.models       import Cosmetic,CreatureSlots,Item,Log
from mysql.session      import Session
from nosql              import *

#
# Routes /map
#
# API: GET /pc/{pcid}
@jwt_required()
def pc_get_one(pcid):
    (code, success, msg, payload) = fn_creature_get(None,pcid)
    if isinstance(code, int):
        return jsonify({"success": success,
                        "msg": msg,
                        "payload": payload}), code

# API: GET /pc/{pcid}/item
@jwt_required()
def pc_item_get_all(creatureid):
    creature = fn_creature_get(None,creatureid)[3]
    session  = Session()

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
        equipment = session.query(CreatureSlots).filter(CreatureSlots.id == creature.id).all()

        feet      = session.query(Item).filter(Item.id == equipment[0].feet).one_or_none()
        hands     = session.query(Item).filter(Item.id == equipment[0].hands).one_or_none()
        head      = session.query(Item).filter(Item.id == equipment[0].head).one_or_none()
        holster   = session.query(Item).filter(Item.id == equipment[0].holster).one_or_none()
        lefthand  = session.query(Item).filter(Item.id == equipment[0].lefthand).one_or_none()
        righthand = session.query(Item).filter(Item.id == equipment[0].righthand).one_or_none()
        shoulders = session.query(Item).filter(Item.id == equipment[0].shoulders).one_or_none()
        torso     = session.query(Item).filter(Item.id == equipment[0].torso).one_or_none()
        legs      = session.query(Item).filter(Item.id == equipment[0].legs).one_or_none()

        # We publicly anounce the cosmetics owned by a PC
        cosmetic  = session.query(Cosmetic)\
                           .filter(Cosmetic.bearer == creature.id)\
                           .all()
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
    finally:
        session.close()

# API: GET /pc/{pcid}/event
@jwt_required()
def pc_event_get_all(creatureid):
    creature = fn_creature_get(None,creatureid)[3]
    session  = Session()

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200

    try:
        log   = session.query(Log)\
                       .filter(Log.src == creature.id)\
                       .order_by(Log.date.desc())\
                       .limit(50)\
                       .all()
    except Exception as e:
        msg = f'Event Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Event Query OK (creatureid:{creature.id})',
                        "payload": log}), 200
    finally:
        session.close()
