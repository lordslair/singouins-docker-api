# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Cosmetic import CosmeticDocument
from mongo.models.Item import ItemDocument
from mongo.models.Satchel import SatchelDocument

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/item/*
#


# API: GET /mypc/<uuid:creatureuuid>/item
@jwt_required()
# Custom decorators
@check_creature_exists
def item_get(creatureuuid):
    try:
        Cosmetics = CosmeticDocument.objects(bearer=g.Creature.id)
        Items = ItemDocument.objects(bearer=g.Creature.id)
        Satchel = SatchelDocument.objects(_id=g.Creature.id)
    except Exception as e:
        msg = f'{g.h} Document(s) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Document(s) Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "armor": [Item.to_mongo() for Item in Items if Item.metatype == 'armor'],
                    "equipment": g.Creature.slots.to_mongo(),
                    "cosmetic": [Cosmetic.to_mongo() for Cosmetic in Cosmetics],
                    "satchel": Satchel.get().to_mongo(),
                    "weapon": [Item.to_mongo() for Item in Items if Item.metatype == 'weapon'],
                },
            }
        ), 200
