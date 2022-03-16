# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request

from mysql.methods.fn_squad     import *
from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: POST /internal/squad
def internal_squad_get_one():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    squadid      = request.json.get('squadid', None)

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
        return jsonify({"success": True,
                        "msg": f'Squad Query OK (squadid:{squadid})',
                        "payload": squad}), 200

# API: GET /internal/squads
def internal_squad_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

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
