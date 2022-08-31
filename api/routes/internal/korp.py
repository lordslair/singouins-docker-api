# -*- coding: utf8 -*-

from flask                 import Flask, jsonify, request
from loguru                import logger

from mysql.methods.fn_korp import *

from variables             import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: GET /internal/korp/{korpid}
def internal_korp_get_one(korpid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if korp:
            return jsonify({"success": True,
                            "msg": f'Korp Query OK (korpid:{korpid})',
                            "payload": korp}), 200
        elif korp is False:
            return jsonify({"success": False,
                            "msg": f'Korp Query KO - Not Found (korpid:{korpid})',
                            "payload": None}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Korp Query KO - Failed (korpid:{korpid})',
                            "payload": None}), 200

# API: GET /internal/korps
def internal_korp_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    try:
        korps = fn_korp_get_all()
    except Exception as e:
        msg = f'Korps Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Korps Query OK',
                        "payload": korps}), 200
