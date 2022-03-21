# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import (fn_creature_add,
                                        fn_creature_del,
                                        fn_creature_get)
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_creatures import fn_creatures_in_all_instances

from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature
def creature_add():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    try:
        creature = fn_creature_add(None,
                                   request.json.get('raceid'),
                                   request.json.get('gender'),
                                   None,
                                   request.json.get('rarity'),
                                   request.json.get('x'),
                                   request.json.get('y'),
                                   request.json.get('instanceid'))
    except Exception as e:
        msg = f'Creature Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'Creature creation OK'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": creature}), 201

# API: DELETE /internal/creature/{creatureid}
def creature_del(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

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
        # Now we can delete tue PC itself
        if fn_creature_del(creature):
            logger.trace('PC delete OK')
    except Exception as e:
        msg = f'Creature delete KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Creature delete OK (creatureid:{creature.id})',
                        "payload": None}), 200

# API: GET /internal/creature/{creatureid}
def creature_get_one(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    try:
        creature = fn_creature_get(None,creatureid)[3]
    except Exception as e:
        msg = f'Creature Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'Creature Query OK'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": creature}), 200

# API: GET /internal/creatures
def creature_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    try:
        creatures = fn_creatures_in_all_instances()
    except Exception as e:
        msg = f'Creatures Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'Creatures Query OK'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": creatures}), 200
