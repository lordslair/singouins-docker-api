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
# API: PUT /internal/creature/{creatureid}/status/{statusmetaid}
def creature_status_add(creatureid,statusmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403
    if not request.is_json:
        msg = f'Missing JSON in request'
        logger.warn(msg)
        return jsonify({"msg": msg, "success": False, "payload": None}), 400

    duration    = request.json.get('duration')

    if not isinstance(duration, int):
        return jsonify({"success": False,
                        "msg": f'Duration should be an INT (duration:{duration})',
                        "payload": None}), 200

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Status add
    try:
        creature_status   = add_status(creature,duration,statusmetaid)
        creature_statuses = get_statuses(creature)
    except Exception as e:
        msg = f'Status Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_status and creature_statuses:
            msg = f'Status add OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"statuses": creature_statuses,
                                        "creature": creature}}), 200
        else:
            msg = f'Status add KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: DELETE /internal/creature/{creatureid}/status/{statusmetaid}
def creature_status_del(creatureid,statusmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Status del
    try:
        creature_status   = del_status(creature,statusmetaid)
        creature_statuses = get_statuses(creature)
    except Exception as e:
        msg = f'Status Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_status > 0:
            msg = f'Status del OK (creatureid:{creature.id},statusmetaid:{statusmetaid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"statuses": creature_statuses,
                                        "creature": creature}}), 200
        elif creature_status == 0:
            msg = f'Status del KO - Status Not Found (creatureid:{creature.id},statusmetaid:{statusmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            msg = f'Status del KO - Failed (creatureid:{creature.id},statusmetaid:{statusmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/status/{statusmetaid}
def creature_status_get_one(creatureid,statusmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Status get
    try:
        creature_status  = get_status(creature,statusmetaid)
    except Exception as e:
        msg = f'Status Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_status is False:
            msg = f'Status get KO - Status Not Found (creatureid:{creature.id},statusmetaid:{statusmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        elif creature_status:
            msg = f'Status get OK (creatureid:{creature.id},statusmetaid:{statusmetaid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"status": creature_status,
                                        "creature": creature}}), 200
        else:
            msg = f'Status get KO - Failed (creatureid:{creature.id},statusmetaid:{statusmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/statuses
def creature_status_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Statuses get
    try:
        creature_statuses = get_statuses(creature)
    except Exception as e:
        msg = f'Statuses Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if isinstance(creature_statuses, list):
            msg = f'Statuses get OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"statuses": creature_statuses,
                                        "creature": creature}}), 200
        else:
            msg = f'Statuses get KO - Failed (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
