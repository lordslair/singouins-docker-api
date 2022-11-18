# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisWallet   import RedisWallet

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/wallet
def creature_wallet(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Creature = RedisCreature().get(creatureid)
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

    try:
        Wallet = RedisWallet(Creature)
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
        if Wallet:
            msg = f'{h} Wallet Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "wallet": Wallet._asdict(),
                        "creature": Creature._asdict(),
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
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Creature = RedisCreature().get(creatureid)
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

    if not isinstance(count, int):
        msg = f'{h} Count should be an INT (count:{count})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if operation not in ['add', 'consume']:
        msg = (f"{h} Operation should be in "
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
        msg = (f"{h} Caliber should be a valid caliber (caliber:{caliber})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Wallet = RedisWallet(Creature)
        if operation == 'consume' and count > 0:
            Wallet.incr(caliber, count * (-1))
        else:
            Wallet.incr(caliber, count)
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
        if Wallet:
            msg = f'{h} Wallet Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "wallet": Wallet._asdict(),
                        "creature": Creature._asdict(),
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
