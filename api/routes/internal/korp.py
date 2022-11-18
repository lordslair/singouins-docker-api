# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisKorp     import RedisKorp

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# API: GET /internal/korp/{korpid}
def internal_korp_get_one(korpid):
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
        if Korp:
            msg = f'[Korp.id:{Korp.id}] Korp Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp._asdict(),
                }
            ), 200
        elif Korp is False:
            msg = f'[Korp.id:{korpid}] Korp Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
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
