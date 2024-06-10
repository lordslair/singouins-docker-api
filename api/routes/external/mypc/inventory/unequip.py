# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from nosql.queue import yqueue_put
from nosql.models.RedisEvent import RedisEvent
from nosql.models.RedisPa import RedisPa

from utils.decorators import (
    check_creature_exists,
    check_creature_pa,
    check_item_exists,
    )

from variables import YQ_BROADCAST

#
# Inventory.unequip specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 0


#
# Routes /mypc/<uuid:creatureuuid>/inventory/*
#
# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/unequip/<string:type>/<string:slotname> # noqa
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
@check_item_exists
def unequip(creatureuuid, type, slotname, itemuuid):
    try:
        if slotname == 'righthand':
            if g.Creature.slots.righthand.id == itemuuid:
                if g.Creature.slots.righthand == g.Creature.slots.lefthand:
                    # The weapon equipped takes both hands
                    g.Creature.slots.righthand = None
                    g.Creature.slots.lefthand = None
                else:
                    g.Creature.slots.righthand = None
        elif slotname == 'lefthand':
            if g.Creature.slots.lefthand.id == itemuuid:
                if g.Creature.slots.righthand == g.Creature.slots.lefthand:
                    # The weapon equipped takes both hands
                    g.Creature.slots.righthand = None
                    g.Creature.slots.lefthand = None
                else:
                    g.Creature.slots.lefthand = None
        else:
            setattr(g.Creature.slots, slotname, None)
    except Exception as e:
        msg = f'{g.h} Unequip KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()

    # We put the info in queue for ws
    yqueue_put(
        YQ_BROADCAST,
        {
            "ciphered": False,
            "payload": g.Creature.to_mongo(),
            "route": "mypc/{id1}/inventory/item/{id2}/unequip/{id3}/{id4}",
            "scope": {
                "id": None,
                "scope": 'broadcast',
                },
            }
        )

    # We create the Creature Event
    RedisEvent().new(
        action_src=g.Creature.id,
        action_dst=None,
        action_type='action/unequip',
        action_text='Unequipped something',
        action_ttl=30 * 86400
        )

    msg = f'{g.h} Unequip OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "red": RedisPa(creatureuuid=creatureuuid).redpa,
                "blue": RedisPa(creatureuuid=creatureuuid).bluepa,
                "equipment": g.Creature.to_mongo(),
            },
        }
    ), 200
