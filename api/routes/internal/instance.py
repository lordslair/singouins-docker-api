# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisInstance import RedisInstance

from utils.routehelper          import (
    request_internal_token_check,
    )

#
# Routes /internal
#


# API: GET /internal/instances
def internal_instance_get_all():
    request_internal_token_check(request)
    h = '[Instance.id:None]'

    try:
        Instances = RedisInstance().search(query='-(@map:None)')
    except Exception as e:
        msg = f'{h} Instances Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Instances Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Instances,
            }
        ), 200
