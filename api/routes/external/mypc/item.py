# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisCosmetic import RedisCosmetic
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisWallet   import RedisWallet


#
# Routes /mypc/{pcid}/item/*
#
# API: GET /mypc/{pcid}/item
@jwt_required()
def item_get(pcid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creatureid:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        creature_inventory = RedisItem(creature).search(
            field='bearer', query=f'[{creature.id} {creature.id}]'
            )

        armor = [x for x in creature_inventory if x['metatype'] == 'armor']
        weapon = [x for x in creature_inventory if x['metatype'] == 'weapon']

        creature_slots = RedisSlots(creature)
        creature_cosmetics = RedisCosmetic(creature).get_all()
        creature_wallet = RedisWallet(creature)
    except Exception as e:
        msg = f'Items Query KO (pcid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'Equipment query successed (pcid:{creature.id})'
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
