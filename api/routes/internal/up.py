# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# API: GET /internal/up
def up_get():
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

    msg = 'UP and running'
    logger.warning(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": None,
        }
    ), 200
