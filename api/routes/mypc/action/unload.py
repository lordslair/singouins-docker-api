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
# Action.unload specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST /mypc/<uuid:creatureuuid>/action/unload/<uuid:itemuuid>
@jwt_required()
# Custom decorators
@check_user_exists
@check_creature_exists
@check_creature_owned
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
@check_item_exists
def unload(creatureuuid, itemuuid):
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
    if g.Item.ammo == 0:
        msg = f'{g.h} Already empty'
        logger.debug(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        # We add the ammo into the Satchel
        Satchel = SatchelDocument.objects().filter(_id=g.Creature.id)
        update_query = {
            f"inc__ammo__{itemmeta['caliber']}": g.Item.ammo,
            "set__updated": datetime.datetime.utcnow(),
            }
        logger.trace(update_query)
        Satchel.update(**update_query)
        # We unload the weapon
        g.Item.ammo = 0
        g.Item.updated = datetime.datetime.utcnow()
        g.Item.save()
        # We consume the PA
        consume_pa(creatureuuid=g.Creature.id, bluepa=PA_COST_BLUE)
    except Exception as e:
        msg = f'{g.h} Unload Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Unload Query OK'
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