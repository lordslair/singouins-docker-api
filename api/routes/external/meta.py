# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import jwt_required

from mysql.methods      import internal_meta_get_one
from nosql              import *

#
# Routes /meta
#
# API: GET /meta/item/{metatype}
@jwt_required()
def external_meta_get_one(metatype):
    # Pre-flight checks
    if not isinstance(metatype, str):
        return jsonify({"success": False,
                        "msg": f'Meta type Malformed (metatype:{metatype}) [Should be a String]',
                        "payload": None}), 200

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
