# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get,fn_creature_position_set

from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/position/{x}/{y}
def creature_position_set(creatureid,x,y):
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
            msg = f'Creature Query KO - Not Found (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        creature    = fn_creature_position_set(creature.id,x,y)
    except Exception as e:
        msg = f'Creature Query KO - Failed (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature:
            return jsonify({"success": True,
                            "msg": f'Creature Query OK (pcid:{creature.id})',
                            "payload": creature}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Creature Query KO - Not Found (pcid:{creature.id})',
                            "payload": None}), 200
