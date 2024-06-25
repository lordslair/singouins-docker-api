# -*- coding: utf8 -*-

import datetime

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.metas                import metaNames
from nosql.models.RedisPa       import RedisPa

from mongo.models.Satchel import SatchelDocument

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    check_user_exists,
    check_creature_owned,
    check_creature_pa,
    )

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
    itemmeta = metaNames[g.Item.metatype][g.Item.metaid]
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
        Satchel.update(**update_query)
        # We unload the weapon
        g.Item.ammo = 0
        g.Item.updated = datetime.datetime.utcnow()
        g.Item.save()
        # We consume the PA
        RedisPa(creatureuuid=creatureuuid).consume(bluepa=PA_COST_BLUE)
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
                    "red": RedisPa(creatureuuid=creatureuuid).as_dict()['red'],
                    "blue": RedisPa(creatureuuid=creatureuuid).as_dict()['blue'],
                    "weapon": g.Item.to_mongo(),
                },
            }
        ), 200
