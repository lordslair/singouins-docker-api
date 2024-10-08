# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Item import ItemDocument

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/inventory/*
#
# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/offset/<int:offsetx>/<int:offsety> # noqa E501
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
def offset(creatureuuid, itemuuid, offsetx=None, offsety=None):

    Items = ItemDocument.objects(bearer=g.Creature.id)

    try:
        g.Item.offsetx = offsetx
        g.Item.offsety = offsety
        g.Item.updated = datetime.datetime.utcnow()
        g.Item.save()
    except Exception as e:
        msg = f'{g.h} Offset Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # JOB IS DONE
    msg = f'{g.h} Offset Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "armor": [Item.to_mongo() for Item in Items if Item.metatype == 'armor'],
                "creature": g.Creature.to_mongo(),
                "weapon": [Item.to_mongo() for Item in Items if Item.metatype == 'weapon'],
            },
        }
    ), 200
