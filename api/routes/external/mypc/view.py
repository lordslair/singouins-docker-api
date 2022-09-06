# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_view      import (fn_creature_view_get,
                                        fn_creature_squad_view_get)


#
# Routes /mypc/{pcid}/view/*
#
# API: GET /mypc/{pcid}/view
@jwt_required()
def view_get(pcid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (pcid:{pcid})'
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
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        if creature.squad is None:
            # PC is solo / not in a squad
            view_final = fn_creature_view_get(creature)
        else:
            # PC is in a squad
            view_final = fn_creature_squad_view_get(creature)
    except Exception as e:
        msg = f'View Query KO (pcid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'View Query OK (creature.id:{creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": view_final,
            }
        ), 200
