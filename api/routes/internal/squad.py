# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request

from mysql.methods.fn_squad     import *
from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: POST /internal/squad/{squadid}
def internal_squad_get_one(squadid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    incr.one('queries:internal:squad')

    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if squad or squad is True:
            return jsonify({"success": True,
                            "msg": f'Squad Query OK (squadid:{squadid})',
                            "payload": squad}), 200
        elif squad is False:
            return jsonify({"success": False,
                            "msg": f'Squad Query KO - Not Found (squadid:{squadid})',
                            "payload": None}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Squad Query KO - Failed (squadid:{squadid})',
                            "payload": None}), 200

# API: GET /internal/squads
def internal_squad_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    incr.one('queries:internal:squads')

    try:
        squads = fn_squad_get_all()
    except Exception as e:
        msg = f'Squads Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Squads Query OK',
                        "payload": squads}), 200
