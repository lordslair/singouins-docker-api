# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisPa       import RedisPa


#
# Routes /mypc/{pcid}/pa/*
#
# API: GET /mypc/{pcid}/pa
@jwt_required()
def pa_get(pcid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creatureid:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        payload = RedisPa(creature).get()
    except Exception as e:
        msg = f'PA Query KO (pcid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": payload,
            }
        ), 200
    else:
        msg = f'PA Query OK (pcid:{creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": payload,
            }
        ), 200
