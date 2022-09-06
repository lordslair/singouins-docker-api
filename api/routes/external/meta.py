# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.metas                import get_meta


#
# Routes /meta
#
# API: GET /meta/item/{metatype}
@jwt_required()
def external_meta_get_one(metatype):
    # Pre-flight checks
    if not isinstance(metatype, str):
        return jsonify(
            {
                "success": True,
                "msg": f'Meta should be a String (metatype:{metatype})',
                "payload": None,
            }
        ), 200

    try:
        meta = get_meta(metatype)
    except Exception as e:
        msg = f'Query KO (metatype:{metatype}) [{e}]'
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
            msg = f'Meta Query KO - Not Found (metatype:{metatype})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
