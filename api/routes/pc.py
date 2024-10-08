# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q

from mongo.models.Cosmetic import CosmeticDocument
from mongo.models.Event import EventDocument

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /pc
#
# API: GET /pc/<uuid:creatureuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
def pc_get_one(creatureuuid):
    msg = f'{g.h} Creatures Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "_id": g.Creature.id,
                "account": g.Creature.account,
                "active": g.Creature.active,
                "created": g.Creature.created,
                "gender": g.Creature.gender,
                "korp": g.Creature.korp.to_mongo(),
                "level": g.Creature.level,
                "name": g.Creature.name,
                "race": g.Creature.race,
                "rarity": g.Creature.rarity,
                "slots": g.Creature.slots.to_mongo(),
                "squad": g.Creature.squad.to_mongo(),
                "updated": g.Creature.updated,
                "xp": g.Creature.xp
            },
        }
    ), 200


# API: GET /pc/{creatureuuid}/item
@jwt_required()
# Custom decorators
@check_creature_exists
def pc_item_get_all(creatureuuid):
    # We answer quite fast if the Creature is a NPC.
    if g.Creature.account is None:
        msg = f'{g.h} Equipment Query OK (NPC)'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "equipment": {},
                    "cosmetic": [],
                    },
            }
        ), 200

    try:
        # We publicly anounce the cosmetics owned by a PC
        Cosmetics = CosmeticDocument.objects(bearer=g.Creature.id).all()
    except Exception as e:
        msg = f'{g.h} Equipment Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    msg = f'{g.h} Equipment Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "equipment": g.Creature.slots.to_mongo(),
                "cosmetic": [Cosmetic.to_mongo() for Cosmetic in Cosmetics],
                },
        }
    ), 200


# API: GET /pc/<uuid:creatureuuid>/event
@jwt_required()
# Custom decorators
@check_creature_exists
def pc_event_get_all(creatureuuid):
    try:
        query = Q(src=creatureuuid) | Q(dst=creatureuuid)
        Events = EventDocument.objects.filter(query)
    except Exception as e:
        msg = f'{g.h} EventDocument Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} EventDocument Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [Event.to_mongo().to_dict() for Event in Events],
            }
        ), 200
