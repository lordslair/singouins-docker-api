# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_view      import fn_creature_view_get,fn_creature_squad_view_get

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: GET /internal/creature/{creatureid}/view
def creature_view_get(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    try:
        creature = fn_creature_get(None,creatureid)[3]
    except Exception as e:
        msg = f'Creature Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if not creature:
            msg = f'Creature Query KO - Not Found (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        if creature.squad is None:
            # Creature is solo / not in a squad
            view_final = fn_creature_view_get(creature)
        else:
            # Creature is in a squad
            view_final = fn_creature_squad_view_get(creature)
    except Exception as e:
        msg = f'View Query KO (creature:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        msg = f'View Query OK (creature:{creature.id})'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg":     msg,
                        "payload": view_final}), 200
