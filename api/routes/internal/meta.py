# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.metas                import get_meta

from utils.routehelper          import (
    request_internal_token_check,
    )

#
# Routes /internal
#


# API: GET /internal/meta
def internal_meta_get_one(metatype):
    request_internal_token_check(request)

    try:
        meta = get_meta(metatype)
    except Exception as e:
        msg = f'Meta Query KO (metatype:{metatype}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if meta:
            msg = f'Meta Query OK (metatype:{metatype})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": meta,
                }
            ), 200
        else:
            msg = f'Meta Query KO - NotFound (metatype:{metatype})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
