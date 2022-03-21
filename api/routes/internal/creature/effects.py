# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql                      import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/effect/{effectmetaid}
def creature_effect_add(creatureid,effectmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    duration     = request.json.get('duration')
    sourceid     = request.json.get('sourceid')

    if not isinstance(duration, int):
        return jsonify({"success": False,
                        "msg": f'Duration should be an INT (duration:{duration})',
                        "payload": None}), 200
    if not isinstance(sourceid, int):
        return jsonify({"success": False,
                        "msg": f'Source ID should be an INT (sourceid:{sourceid})',
                        "payload": None}), 200

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200
    source      = fn_creature_get(None,sourceid)[3]
    if source is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (sourceid:{sourceid})',
                        "payload": None}), 200

    # Effect add
    try:
        creature_effect  = add_effect(creature,duration,effectmetaid,source)
        creature_effects = get_effects(creature)
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_effect and creature_effects:
            msg = f'Effect add OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"effects": creature_effects,
                                        "creature": creature}}), 200
        else:
            msg = f'Effect add KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: DELETE /internal/creature/{creatureid}/effect/{effectid}
def creature_effect_del(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Effect del
    try:
        creature_effect  = del_effect(creature,effectid)
        creature_effects = get_effects(creature)
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_effect > 0:
            msg = f'Effect del OK (creatureid:{creature.id},effectid:{effectid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"effects": creature_effects,
                                        "creature": creature}}), 200
        elif creature_effect == 0:
            msg = f'Effect del KO - Effect Not Found (creatureid:{creature.id},effectid:{effectid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            msg = f'Effect del KO - Failed (creatureid:{creature.id},effectid:{effectid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/effect/{effectid}
def creature_effect_get_one(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Effect get
    try:
        creature_effect  = get_effect(creature,effectid)
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_effect is False:
            msg = f'Effect get KO - Effect Not Found (creatureid:{creature.id},effectid:{effectid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        elif creature_effect:
            msg = f'Effect get OK (creatureid:{creature.id},effectid:{effectid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"effect": creature_effect,
                                        "creature": creature}}), 200
        else:
            msg = f'Effect get KO - Failed (creatureid:{creature.id},effectid:{effectid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/effects
def creature_effect_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Effects get
    try:
        creature_effects = get_effects(creature)
    except Exception as e:
        msg = f'Effects Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if isinstance(creature_effects, list):
            msg = f'Effects get OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"effects": creature_effects,
                                        "creature": creature}}), 200
        else:
            msg = f'Effects get KO - Failed (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
