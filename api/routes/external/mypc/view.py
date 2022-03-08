# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_view      import fn_creature_view_get,fn_creature_squad_view_get

from nosql                      import *

#
# Routes /mypc/{pcid}/stats
#
# API: GET /mypc/{pcid}/stats
@jwt_required()
def view_get(pcid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if user is None:
        return jsonify({"success": False,
                        "msg": f'User not found (user:{user})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409

    try:
        if pc.squad is None:
            # PC is solo / not in a squad
            view_final = fn_creature_view_get(pc)
        else:
            # PC is in a squad
            view_final = fn_creature_squad_view_get(pc)
    except Exception as e:
        msg = f'View Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'View Query OK (pcid:{pc.id})',
                        "payload": view_final}), 200
