# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisWallet   import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: GET /internal/creature/{creatureid}/wallet
def creature_wallet(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

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
            msg = f'Creature Query KO - Not Found (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        creature_wallet = RedisWallet(creature)
    except Exception as e:
        msg = f'Wallet Query KO - Failed (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_wallet:
            return jsonify({"success": True,
                            "msg": f'Wallet Query OK (pcid:{creature.id})',
                            "payload": {"wallet":   creature_wallet._asdict(),
                                        "creature": creature}}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Wallet Query KO - Not Found (pcid:{creature.id})',
                            "payload": None}), 200

# API: PUT /internal/creature/{creatureid}/wallet/{caliber}/{operation}/(count)
def creature_wallet_modify(creatureid,caliber,operation,count):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    if not isinstance(count, int):
        return jsonify({"success": False,
                        "msg": f'Count should be an INT (count:{count})',
                        "payload": None}), 200
    if operation not in ['add','consume']:
        return jsonify({"success": False,
                        "msg": f"Operation should be in ['add','consume'] (operation:{operation})",
                        "payload": None}), 200
    if caliber not in ['cal22','cal223','cal311','cal50','cal55','shell','bolt','arrow']:
        return jsonify({"success": False,
                        "msg": f"Count should be in in ['cal22','cal223','cal311','cal50','cal55','shell','bolt','arrow'] (caliber:{caliber})",
                        "payload": None}), 200

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
            msg = f'Creature Query KO - Not Found (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        creature_wallet = RedisWallet(creature)
        if operation == 'consume' and count > 0:
            creature_wallet.incr(caliber, count * (-1))
        else:
            creature_wallet.incr(caliber, count)
    except Exception as e:
        msg = f'Wallet Query KO - Failed (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_wallet:
            return jsonify({"success": True,
                            "msg": f'Wallet Query OK (pcid:{creature.id})',
                            "payload": {"wallet":   creature_wallet._asdict(),
                                        "creature": creature}}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Wallet Query KO - Not Found (pcid:{creature.id})',
                            "payload": None}), 200
