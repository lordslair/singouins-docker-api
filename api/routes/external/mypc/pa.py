# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity

from mysql.methods      import fn_creature_get,fn_user_get
from nosql              import *

#
# Routes /mypc/{pcid}/pa
#
# API: GET /mypc/{pcid}/pa
@jwt_required()
def pa_get(pcid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409

    try:
        payload = get_pa(pcid)[3]
    except Exception as e:
        msg = f'PA Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'PA Query OK (pcid:{pc.id})',
                        "payload": payload}), 200
