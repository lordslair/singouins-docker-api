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
        logger.warn(msg)
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
        redis_wallet    = RedisWallet(creature)
        creature_wallet = redis_wallet.dict
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
                            "payload": {"wallet":   creature_wallet,
                                        "creature": creature}}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Wallet Query KO - Not Found (pcid:{creature.id})',
                            "payload": None}), 200

# API: PUT /internal/creature/{creatureid}/wallet/{caliber}/{operation}/(count)
def creature_wallet_modify(creatureid,caliber,operation,count):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
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
        redis_wallet    = RedisWallet(creature)
        if operation == 'consume' and count > 0:
            if   caliber == 'cal22':  redis_wallet.cal22  -= count
            elif caliber == 'cal223': redis_wallet.cal223 -= count
            elif caliber == 'cal311': redis_wallet.cal311 -= count
            elif caliber == 'cal50':  redis_wallet.cal50  -= count
            elif caliber == 'cal55':  redis_wallet.cal55  -= count
            elif caliber == 'shell':  redis_wallet.shell  -= count
            elif caliber == 'bolt':   redis_wallet.bolt   -= count
            elif caliber == 'arrow':  redis_wallet.arrow  -= count
        else:
            if   caliber == 'cal22':  redis_wallet.cal22  += count
            elif caliber == 'cal223': redis_wallet.cal223 += count
            elif caliber == 'cal311': redis_wallet.cal311 += count
            elif caliber == 'cal50':  redis_wallet.cal50  += count
            elif caliber == 'cal55':  redis_wallet.cal55  += count
            elif caliber == 'shell':  redis_wallet.shell  += count
            elif caliber == 'bolt':   redis_wallet.bolt   += count
            elif caliber == 'arrow':  redis_wallet.arrow  += count

        # This returns True if the HASH is properly stored in Redis
        stored_wallet     = redis_wallet.store()
        redis_wallet_new  = redis_wallet.refresh()
    except Exception as e:
        msg = f'Wallet Query KO - Failed (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if stored_wallet and redis_wallet_new:
            return jsonify({"success": True,
                            "msg": f'Wallet Query OK (pcid:{creature.id})',
                            "payload": {"wallet":   redis_wallet_new.dict,
                                        "creature": creature}}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Wallet Query KO - Not Found (pcid:{creature.id})',
                            "payload": None}), 200
