# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisWallet   import RedisWallet

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
        Items = RedisSearch().item(
            query=f"@bearer:{g.Creature.id.replace('-', ' ')}"
            )
        Cosmetics = RedisSearch().cosmetic(
            query=f"@bearer:{g.Creature.id.replace('-', ' ')}"
            )

        Slots = RedisSlots(creatureuuid=g.Creature.id)
        Wallet = RedisWallet(creatureuuid=g.Creature.id)
    except Exception as e:
        msg = f'{g.h} Items Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Items Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "weapon": [
                        Item.as_dict() for Item in Items.results
                        if Item.metatype == 'weapon'
                        ],
                    "armor": [
                        Item.as_dict() for Item in Items.results
                        if Item.metatype == 'armor'
                        ],
                    "equipment": Slots.as_dict(),
                    "cosmetic": [
                        Cosmetic.as_dict() for Cosmetic in Cosmetics.results
                        ],
                    "wallet": Wallet.as_dict(),
                },
            }
        ), 200
