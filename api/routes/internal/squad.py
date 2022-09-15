# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_squad     import fn_squad_get_all, fn_squad_get_one

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# API: POST /internal/squad/{squadid}
def internal_squad_get_one(squadid):
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

    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if squad or squad is True:
            msg = f'Squad Query OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200
        elif squad is False:
            msg = f'Squad Query KO - NotFound (squadid:{squadid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'Squad Query KO (squadid:{squadid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/squads
def internal_squad_get_all():
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

    try:
        squads = fn_squad_get_all()
    except Exception as e:
        msg = f'Squads Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = 'Squads Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": squads,
            }
        ), 200
