# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisKorp     import RedisKorp

from utils.routehelper          import (
    request_internal_token_check,
    )

#
# Routes /internal
#


# API: GET /internal/korp/{korpid}
def internal_korp_get_one(korpid):
    request_internal_token_check(request)

    try:
        Korp = RedisKorp().get(korpid)
    except Exception as e:
        msg = f'[Korp.id:{korpid}] Korp Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Korp is False or Korp is None:
            msg = f'[Korp.id:{korpid}] Korp Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 404

    try:
        korp = Korp.id.replace('-', ' ')
        KorpMembers = RedisCreature().search(
            f"(@korp:{korp}) & (@korp_rank:-Pending)"
            )
        KorpPending = RedisCreature().search(
            f"(@korp:{korp}) & (@korp_rank:Pending)"
            )
    except Exception as e:
        msg = f'[Korp.id:{korpid}] Korp Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if KorpMembers and KorpPending:
            msg = f'[Korp.id:{Korp.id}] Korp Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "members": KorpMembers,
                        "pending": KorpPending,
                        "korp": Korp._asdict(),
                        }
                }
            ), 200
        else:
            msg = f'[Korp.id:{korpid}] Korp Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/korps
def internal_korp_get_all():
    request_internal_token_check(request)

    try:
        Korps = RedisKorp().search(query='-(@instance:None)')
    except Exception as e:
        msg = f'[Korp.id:None] Korps Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = '[Korp.id:None] Korps Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Korps,
            }
        ), 200
