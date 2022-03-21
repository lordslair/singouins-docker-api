# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_inventory import fn_wallet_get

from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/wallet
def creature_wallet(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    # Pre-flight checks
    try:
        creature = fn_creature_get(None,creatureid)[3]
    except Exception as e:
        msg = f'Creature Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if not creature:
            msg = f'Creature Query KO - Not Found (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        wallet    = fn_wallet_get(creature)
    except Exception as e:
        msg = f'Wallet Query KO - Failed (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if wallet:
            return jsonify({"success": True,
                            "msg": f'Wallet Query OK (pcid:{creature.id})',
                            "payload": wallet}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Wallet Query KO - Not Found (pcid:{creature.id})',
                            "payload": None}), 200
