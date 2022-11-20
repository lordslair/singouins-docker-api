# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisCosmetic import RedisCosmetic
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisSlots    import RedisSlots


#
# Routes /pc
#
# API: GET /pc/{pcid}
@jwt_required()
def pc_get_one(creatureid):
    h = f'[Creature.id:{creatureid}]'  # Header for logging
    try:
        Creature = RedisCreature().get(creatureid)
    except Exception as e:
        msg = f'{h} Creature Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
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

    try:
        creature_slots = RedisSlots(Creature)

        feet      = RedisItem(Creature).get(creature_slots.feet)
        hands     = RedisItem(Creature).get(creature_slots.hands)
        head      = RedisItem(Creature).get(creature_slots.head)
        holster   = RedisItem(Creature).get(creature_slots.holster)
        lefthand  = RedisItem(Creature).get(creature_slots.lefthand)
        righthand = RedisItem(Creature).get(creature_slots.righthand)
        shoulders = RedisItem(Creature).get(creature_slots.shoulders)
        torso     = RedisItem(Creature).get(creature_slots.torso)
        legs      = RedisItem(Creature).get(creature_slots.legs)

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
    else:
        pass

    feetmetaid      = feet.metaid      if feet      else None
    handsmetaid     = hands.metaid     if hands     else None
    headmetaid      = head.metaid      if head      else None
    holstermetaid   = holster.metaid   if holster   else None
    shouldersmetaid = shoulders.metaid if shoulders else None
    torsometaid     = torso.metaid     if torso     else None
    legsmetaid      = legs.metaid      if legs      else None

    if righthand and lefthand:
        # PC has 2 weapons equipped.
        if righthand.id == lefthand.id:
            # PC has ONE two-handed weapon equipped.
            # I send only meta inside RH
            righthandmetaid = righthand.metaid
            lefthandmetaid  = None
        else:
            # PC has TWO different weapons equipped.
            righthandmetaid = righthand.metaid
            lefthandmetaid  = lefthand.metaid
    else:
        # PC has 1 or 0 weapons equipped.
        righthandmetaid = righthand.metaid if righthand else None
        lefthandmetaid  = lefthand.metaid  if lefthand  else None

    feetmetatype      = feet.metatype      if feet      else None
    handsmetatype     = hands.metatype     if hands     else None
    headmetatype      = head.metatype      if head      else None
    holstermetatype   = holster.metatype   if holster   else None
    lefthandmetatype  = lefthand.metatype  if lefthand  else None
    righthandmetatype = righthand.metatype if righthand else None
    shouldersmetatype = shoulders.metatype if shoulders else None
    torsometatype     = torso.metatype     if torso     else None
    legsmetatype      = legs.metatype      if legs      else None

    metas = {
        "feet": {
            "metaid": feetmetaid,
            "metatype": feetmetatype,
        },
        "hands": {
            "metaid": handsmetaid,
            "metatype": handsmetatype
        },
        "head": {
            "metaid": headmetaid,
            "metatype": headmetatype
        },
        "holster": {
            "metaid": holstermetaid,
            "metatype": holstermetatype
        },
        "lefthand": {
            "metaid": lefthandmetaid,
            "metatype": lefthandmetatype
        },
        "righthand": {
            "metaid": righthandmetaid,
            "metatype": righthandmetatype
        },
        "shoulders": {
            "metaid": shouldersmetaid,
            "metatype": shouldersmetatype
        },
        "torso": {
            "metaid": torsometaid,
            "metatype": torsometatype
        },
        "legs": {
            "metaid": legsmetaid,
            "metatype": legsmetatype
        },
    }

    msg = f'{h} Equipment Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {"equipment": metas,
                        "cosmetic": creature_cosmetics},
        }
    ), 200


# API: GET /pc/{pcid}/event
@jwt_required()
def pc_event_get_all(creatureid):
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
