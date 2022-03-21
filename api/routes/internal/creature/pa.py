# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisPa       import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: GET /internal/creature/{creatureid}/pa
def creature_pa_get(creatureid):
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

    try:
        creature_pa = RedisPa.get(creature)
    except Exception as e:
        msg = f'PA Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_pa:
            msg = f'PA Query OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"pa": creature_pa,
                                        "creature": creature}}), 200
        else:
            msg = f'PA Query KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: PUT /internal/creature/{creatureid}/pa/consume/{redpa}/{bluepa}
def creature_pa_consume(creatureid,redpa,bluepa):
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

    if redpa > 16 or bluepa > 8:
        msg = f'Cannot consume more than max PA (creatureid:{creature.id},redpa:{redpa},bluepa:{bluepa})'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    if redpa < 0 or bluepa < 0:
        msg = f'Cannot consume PA < 0  (creatureid:{creature.id},redpa:{redpa},bluepa:{bluepa})'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    if redpa >= RedisPa.get(creature)['red']['pa'] or bluepa >= RedisPa.get(creature)['blue']['pa']:
        msg = f'Cannot consume that amount of PA (creatureid:{creature.id},redpa:{redpa},bluepa:{bluepa})'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        ret         = RedisPa.set(creature,redpa,bluepa)
        creature_pa = RedisPa.get(creature)
    except Exception as e:
        msg = f'PA Query KO - Failed (creatureid:{creatureid},redpa:{redpa},bluepa:{bluepa})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if ret:
            msg = f'PA Query OK (creatureid:{creatureid},redpa:{redpa},bluepa:{bluepa})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"pa": creature_pa,
                                        "creature": creature}}), 200
        else:
            msg = f'PA Query KO (creatureid:{creatureid},redpa:{redpa},bluepa:{bluepa})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: POST /internal/creature/{creatureid}/pa/reset
def creature_pa_reset(creatureid):
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

    try:
        ret         = RedisPa.reset(creature)
        creature_pa = RedisPa.get(creature)
    except Exception as e:
        msg = f'PA Query KO - Failed (creatureid:{creatureid})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if ret:
            msg = f'PA Query OK (creatureid:{creatureid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"pa": creature_pa,
                                        "creature": creature}}), 200
        else:
            msg = f'PA Query KO (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
