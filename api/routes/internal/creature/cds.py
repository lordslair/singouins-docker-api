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
# API: PUT /internal/creature/{creatureid}/cd/{skillmetaid}
def creature_cd_add(creatureid,skillmetaid):
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

    # CD add
    try:
        creature_cd  = add_cd(creature,duration,skillmetaid)
        creature_cds = get_cds(creature)
    except Exception as e:
        msg = f'CD Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_cd and creature_cds:
            msg = f'CD add OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"cds": creature_cds,
                                        "creature": creature}}), 200
        else:
            msg = f'CD add KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: DELETE /internal/creature/{creatureid}/cd/{skillmetaid}
def creature_cd_del(creatureid,skillmetaid):
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

    # CD del
    try:
        creature_cd  = del_cd(creature,skillmetaid)
        creature_cds = get_cds(creature)
    except Exception as e:
        msg = f'CD Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_cd > 0:
            msg = f'CD del OK (creatureid:{creature.id},skillmetaid:{skillmetaid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"cds": creature_cds,
                                        "creature": creature}}), 200
        elif creature_cd == 0:
            msg = f'CD del KO - CD Not Found (creatureid:{creature.id},skillmetaid:{skillmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            msg = f'CD del KO - Failed (creatureid:{creature.id},skillmetaid:{skillmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/cd/{skillmetaid}
def creature_cd_get_one(creatureid,skillmetaid):
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

    # CD get
    try:
        creature_cd  = get_cd(creature,skillmetaid)
    except Exception as e:
        msg = f'CD Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_cd is False:
            msg = f'CD get KO - CD Not Found (creatureid:{creature.id},skillmetaid:{skillmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        elif creature_cd:
            msg = f'CD get OK (creatureid:{creature.id},skillmetaid:{skillmetaid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"cd": creature_cd,
                                        "creature": creature}}), 200
        else:
            msg = f'CD get KO - Failed (creatureid:{creature.id},skillmetaid:{skillmetaid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/cds
def creature_cd_get_all(creatureid):
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

    # CDs get
    try:
        creature_cds = get_cds(creature)
    except Exception as e:
        msg = f'CDs Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if isinstance(creature_cds, list):
            msg = f'CDs get OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"cds": creature_cds,
                                        "creature": creature}}), 200
        else:
            msg = f'CDs get KO - Failed (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
