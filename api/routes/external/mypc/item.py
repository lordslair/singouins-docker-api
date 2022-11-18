# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCosmetic import RedisCosmetic
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisWallet   import RedisWallet
from nosql.models.RedisUser     import RedisUser


#
# Routes /mypc/{pcid}/item/*
#
# API: GET /mypc/{pcid}/item
@jwt_required()
def item_get(pcid):
    Creature = RedisCreature().get(pcid)
    User = RedisUser().get(get_jwt_identity())

    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging
    if Creature.account != User.id:
        msg = (f'{h} Token/username mismatch (username:{User.name})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        bearer = Creature.id.replace('-', ' ')
        creature_inventory = RedisItem(Creature).search(
            field='bearer', query=f'{bearer}'
            )

        armor = [x for x in creature_inventory if x['metatype'] == 'armor']
        weapon = [x for x in creature_inventory if x['metatype'] == 'weapon']

        creature_slots = RedisSlots(Creature)
        creature_cosmetics = RedisCosmetic(Creature).get_all()
        creature_wallet = RedisWallet(Creature)
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
                    "weapon": weapon,
                    "armor": armor,
                    "equipment": creature_slots._asdict(),
                    "cosmetic": creature_cosmetics,
                    "wallet": creature_wallet._asdict(),
                },
            }
        ), 200
