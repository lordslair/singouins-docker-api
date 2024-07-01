# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from nosql.queue import yqueue_put

from nosql.models.RedisPa import RedisPa

from mongo.models.Creature import CreatureSlot

from utils.decorators import (
    check_creature_exists,
    check_creature_pa,
    check_item_exists,
    )

from variables import metaNames, YQ_BROADCAST

#
# Inventory.equip specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2


#
# Routes /mypc/<uuid:creatureuuid>/inventory/*
#
# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/equip/<string:type>/<string:slotname> # noqa
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
@check_item_exists
def equip(creatureuuid, type, slotname, itemuuid):
    itemmeta = [x for x in metaNames[type] if x['_id'] == g.Item.metaid][0]
    sizex, sizey = itemmeta['size'].split("x")

    # Pre-requisite checks
    for carac in ['m', 'r', 'g', 'v', 'p', 'b']:
        needed = itemmeta[f'min_{carac}']
        stat = getattr(g.Creature.stats.total, carac)
        if needed > stat:
            msg = f"{g.h} {carac.upper()} prequisites KO (min_{carac}:{needed} > {carac}:{stat})"
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    try:
        logger.trace(f"{g.h} Equip Query >> {slotname}")
        if slotname == 'holster':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the holster
                g.Creature.slots.holster = CreatureSlot(
                    id=g.Item.id,
                    metaid=g.Item.metaid,
                    metatype=g.Item.metatype,
                    )
            else:
                msg = f"{g.h} Item does not fit in holster (size:{itemmeta['size']})"
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        elif slotname == 'righthand':
            if g.Creature.slots.righthand:
                # Something is already equipped in RH
                equippedMeta = metaNames['weapon'][g.Creature.slots.righthand.metaid]
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    if equippedMeta['onehanded'] is True:
                        # A 1H weapons is in RH : we replace
                        g.Creature.slots.righthand = CreatureSlot(
                            id=g.Item.id,
                            metaid=g.Item.metaid,
                            metatype=g.Item.metatype,
                            )
                    if equippedMeta['onehanded'] is False:
                        # A 2H weapons is in RH & LH
                        # We replace RH and clean LH
                        g.Creature.slots.righthand = CreatureSlot(
                            id=g.Item.id,
                            metaid=g.Item.metaid,
                            metatype=g.Item.metatype,
                            )
                        g.Creature.slots.lefthand = None
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    g.Creature.slots.righthand = CreatureSlot(
                        id=g.Item.id,
                        metaid=g.Item.metaid,
                        metatype=g.Item.metatype,
                        )
                    g.Creature.slots.lefthand = CreatureSlot(
                        id=g.Item.id,
                        metaid=g.Item.metaid,
                        metatype=g.Item.metatype,
                        )
            else:
                # Nothing in RH
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    g.Creature.slots.righthand = CreatureSlot(
                        id=g.Item.id,
                        metaid=g.Item.metaid,
                        metatype=g.Item.metatype,
                        )
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    g.Creature.slots.righthand = CreatureSlot(
                        id=g.Item.id,
                        metaid=g.Item.metaid,
                        metatype=g.Item.metatype,
                        )
                    g.Creature.slots.lefthand = CreatureSlot(
                        id=g.Item.id,
                        metaid=g.Item.metaid,
                        metatype=g.Item.metatype,
                        )
        elif slotname == 'lefthand':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the left hand
                g.Creature.slots.lefthand = CreatureSlot(
                    id=g.Item.id,
                    metaid=g.Item.metaid,
                    metatype=g.Item.metatype,
                    )
            else:
                msg = f"{g.h} Item does not fit in left hand (size:{itemmeta['size']})"
                logger.trace(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        else:
            setattr(
                g.Creature.slots,
                slotname,
                CreatureSlot(
                    id=g.Item.id,
                    metaid=g.Item.metaid,
                    metatype=g.Item.metatype,
                    )
                )
    except Exception as e:
        msg = (f'{g.h} Equip Query KO [{e}]')
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

    # Here everything should be OK with the equip
    # We consume the red PA (costpa) right now
    RedisPa(creatureuuid=creatureuuid).consume(redpa=PA_COST_BLUE)

    # We put the info in queue for ws
    try:
        qmsg = {
            "ciphered": False,
            "payload": g.Creature.to_mongo(),
            "route": "mypc/{id1}/inventory/item/{id2}/equip/{id3}/{id4}",
            "scope": {
                "id": None,
                "scope": 'broadcast',
                },
            }
        yqueue_put(YQ_BROADCAST, jsonify(qmsg).get_data(as_text=True))
    except Exception as e:
        msg = (f'{g.h} Equip Queue KO [{e}]')
        logger.error(msg)

    # JOB IS DONE
    msg = f'{g.h} Equip Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "red": RedisPa(creatureuuid=creatureuuid).redpa,
                "blue": RedisPa(creatureuuid=creatureuuid).bluepa,
                "creature": g.Creature.to_mongo(),
            },
        }
    ), 200
