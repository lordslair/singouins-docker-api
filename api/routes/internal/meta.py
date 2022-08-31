# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from loguru             import logger

from nosql              import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: GET /internal/meta
def internal_meta_get_one(metatype):
    # Pre-flight checks
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    try:
        meta = metas.get_meta(metatype)
    except Exception as e:
        msg = f'Query KO (metatype:{metatype}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if meta:
            return jsonify({"success": True,
                            "msg": f'Query OK (metatype:{metatype})',
                            "payload": meta}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Meta not found (metatype:{metatype})',
                            "payload": None}), 200
