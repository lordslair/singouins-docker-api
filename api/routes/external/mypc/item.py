# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisWallet   import RedisWallet

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/<uuid:creatureuuid>/item/*
#


# API: GET /mypc/<uuid:creatureuuid>/item
@jwt_required()
def item_get(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Items = RedisSearch().item(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
            )
        Cosmetics = RedisSearch().cosmetic(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
            )

        Slots = RedisSlots(creatureuuid=Creature.id)
        Wallet = RedisWallet(creatureuuid=Creature.id)
    except Exception as e:
        msg = f'{h} Items Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Items Query OK'
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
