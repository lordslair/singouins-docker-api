# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_inventory import *
from mysql.methods.fn_user      import fn_user_get

from nosql                      import *

#
# Routes /mypc/{pcid}/item
#
# API: GET /mypc/{pcid}/item
@jwt_required()
def item_get(pcid):
    creature = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200
    if creature.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                        "payload": None}), 409

    try:
        all_items_sql  = fn_item_get_all(creature)
        all_items_json = json.loads(jsonify(all_items_sql).get_data())

        armor     = [x for x in all_items_json if x['metatype'] == 'armor']
        slots     = fn_slots_get_all(creature)
        cosmetic  = fn_cosmetics_get_all(creature)
        wallet    = [fn_wallet_get(creature)]
        weapon    = [x for x in all_items_json if x['metatype'] == 'weapon']
    except Exception as e:
        msg = f'Items Query KO (pcid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Equipment query successed (pcid:{creature.id})',
                        "payload": {"weapon":    weapon,
                                    "armor":     armor,
                                    "equipment": slots,
                                    "cosmetic":  cosmetic,
                                    "wallet":    wallet}}), 200
