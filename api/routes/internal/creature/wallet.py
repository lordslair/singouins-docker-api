# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisWallet   import RedisWallet

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/wallet
def creature_wallet(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        creature_wallet = RedisWallet(creature)
    except Exception as e:
        msg = f'{h} Wallet Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_wallet:
            msg = f'{h} Wallet Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "wallet": creature_wallet._asdict(),
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Wallet Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: PUT /internal/creature/{creatureid}/wallet/{caliber}/{operation}/(count)
def creature_wallet_modify(creatureid, caliber, operation, count):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    if not isinstance(count, int):
        msg = f'Count should be an INT (count:{count})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if operation not in ['add', 'consume']:
        msg = (f"Operation should be in "
               f"['add','consume'] (operation:{operation})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if caliber not in ['cal22',
                       'cal223',
                       'cal311',
                       'cal50',
                       'cal55',
                       'shell',
                       'bolt',
                       'arrow',
                       ]:
        msg = (f"Caliber should be a valid caliber (caliber:{caliber})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        creature_wallet = RedisWallet(creature)
        if operation == 'consume' and count > 0:
            creature_wallet.incr(caliber, count * (-1))
        else:
            creature_wallet.incr(caliber, count)
    except Exception as e:
        msg = f'{h} Wallet Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_wallet:
            msg = f'{h} Wallet Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "wallet": creature_wallet._asdict(),
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Wallet Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
