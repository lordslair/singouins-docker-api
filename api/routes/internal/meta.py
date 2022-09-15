# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.metas                import get_meta

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# API: GET /internal/meta
def internal_meta_get_one(metatype):
    # Pre-flight checks
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
