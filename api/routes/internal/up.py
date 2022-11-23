# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from utils.routehelper          import (
    request_internal_token_check,
    )

#
# Routes /internal
#


# API: GET /internal/up
def up_get():
    request_internal_token_check(request)

    msg = 'UP and running'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": None,
        }
    ), 200
