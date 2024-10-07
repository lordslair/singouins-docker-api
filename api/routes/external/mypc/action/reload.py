# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Satchel import SatchelDocument

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    check_user_exists,
    check_creature_owned,
    check_creature_pa,
    )
from utils.redis import get_pa, consume_pa
from variables import metaNames

#
# Action.reload specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST /mypc/<uuid:creatureuuid>/action/reload/<uuid:itemuuid>
@jwt_required()
# Custom decorators
@check_user_exists
@check_creature_exists
@check_creature_owned
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
@check_item_exists
def reload(creatureuuid, itemuuid):
    itemmeta = [x for x in metaNames[g.Item.metatype] if x['_id'] == g.Item.metaid][0]
    if itemmeta['pas_reload'] is None:
        msg = f'{g.h} Not reloadable'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if g.Item.ammo == itemmeta['max_ammo']:
        msg = f"{g.h} Already loaded ({g.Item.ammo}/{itemmeta['max_ammo']})"
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Satchel = SatchelDocument.objects().filter(_id=g.Creature.id).get()

        # We calculate the amount of needed ammo to reload
        ownedammo = getattr(Satchel.ammo, itemmeta['caliber'])
        neededammo = itemmeta['max_ammo'] - g.Item.ammo
        details = f"(cal:{itemmeta['caliber']}, ammo:{neededammo}/{ownedammo})"

        if ownedammo < neededammo:
            msg = f"{g.h} Not enough Ammo to reload {details}"
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.trace(f"{g.h} Enough Ammo to reload {details}")

        # We reload the weapon
        g.Item.ammo = itemmeta['max_ammo']
        g.Item.updated = datetime.datetime.utcnow()
        g.Item.save()
        # We remove the ammo from Satchel
        Satchel = SatchelDocument.objects().filter(_id=g.Creature.id)
        update_query = {
            f"inc__ammo__{itemmeta['caliber']}": -neededammo,
            "set__updated": datetime.datetime.utcnow(),
            }
        Satchel.update(**update_query)
        # We consume the PA
        consume_pa(creatureuuid=g.Creature.id, bluepa=PA_COST_BLUE)
    except Exception as e:
        msg = f'{g.h} Reload Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Reload Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": get_pa(creatureuuid=g.Creature.id)['red'],
                    "blue": get_pa(creatureuuid=g.Creature.id)['blue'],
                    "weapon": g.Item.to_mongo(),
                },
            }
        ), 200
