# -*- coding: utf8 -*-

import json

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_inventory import (fn_item_get_all,
                                        )
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisCosmetic import RedisCosmetic
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
        all_items_sql = fn_item_get_all(creature)
        all_items_json = json.loads(jsonify(all_items_sql).get_data())

        armor = [x for x in all_items_json if x['metatype'] == 'armor']
        creature_slots = RedisSlots(creature)
        creature_cosmetics = RedisCosmetic(creature).get_all()
        creature_wallet = RedisWallet(creature)
        weapon = [x for x in all_items_json if x['metatype'] == 'weapon']
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
