# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisStatus   import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/status/{status_name}
def creature_status_add(creatureid,status_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403
    if not request.is_json:
        msg = f'Missing JSON in request'
        logger.warn(msg)
        return jsonify({"msg": msg, "success": False, "payload": None}), 400

    duration    = request.json.get('duration')
    extra       = request.json.get('extra')
    source      = request.json.get('source')

    if not isinstance(duration, int):
        return jsonify({"success": False,
                        "msg": f'Duration should be an INT (duration:{duration})',
                        "payload": None}), 200
    if not isinstance(source, int):
        return jsonify({"success": False,
                        "msg": f'Source should be an INT (source:{source})',
                        "payload": None}), 200

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Status add
    try:
        redis_status = RedisStatus(creature)

        redis_status.duration_base = duration
        redis_status.extra         = extra
        redis_status.name          = status_name
        redis_status.source        = source

        # This returns True if the HASH is properly stored in Redis
        stored_status     = redis_status.store()
        creature_statuses = redis_status.get_all()
    except Exception as e:
        msg = f'Status Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if stored_status and creature_statuses:
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

# API: DELETE /internal/creature/{creatureid}/status/{status_name}
def creature_status_del(creatureid,status_name):
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
        redis_status      = RedisStatus(creature)
        deleted_status    = redis_status.destroy(status_name)
        creature_statuses = redis_status.get_all()
    except Exception as e:
        msg = f'Status Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if deleted_status:
            msg = f'Status del OK (creatureid:{creature.id},status_name:{status_name})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"statuses": creature_statuses,
                                        "creature": creature}}), 200
        else:
            msg = f'Status del KO - Failed (creatureid:{creature.id},status_name:{status_name})'
            logger.error(msg)
            return warning({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/status/{status_name}
def creature_status_get_one(creatureid,status_name):
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
        redis_status    = RedisStatus(creature)
        creature_status = redis_status.get(status_name)
    except Exception as e:
        msg = f'Status Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_status is False:
            msg = f'Status get KO - Status Not Found (creatureid:{creature.id},status_name:{status_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        elif creature_status:
            msg = f'Status get OK (creatureid:{creature.id},status_name:{status_name})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg": msg,
                            "payload": {"status": creature_status.dict,
                                        "creature": creature}}), 200
        else:
            msg = f'Status get KO - Failed (creatureid:{creature.id},status_name:{status_name})'
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
        redis_status      = RedisStatus(creature)
        creature_statuses = redis_status.get_all()
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
