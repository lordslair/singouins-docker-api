# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisPa       import *
from nosql.models.RedisStats    import *

#
# Routes /mypc/{pcid}/stats
#
# API: GET /mypc/{pcid}/stats
@jwt_required()
def stats_get(pcid):
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
        # We check if we have the data in redis
        creature_stats  = RedisStats(pc)
    except Exception as e:
        msg = f'Stats Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Stats Query OK (pcid:{pc.id})',
                        "payload": creature_stats.dict}), 200
