# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisWallet   import RedisWallet

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/wallet
def creature_wallet(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    try:
        Wallet = RedisWallet(Creature.id)
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
                        "wallet": Wallet.as_dict(),
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
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

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
        Wallet = RedisWallet(Creature.id)
        if operation == 'consume' and count > 0:
            wallet_value = getattr(Wallet, caliber)
            setattr(Wallet, caliber, wallet_value - count)
        else:
            setattr(Wallet, caliber, count)
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
                        "wallet": Wallet.as_dict(),
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
