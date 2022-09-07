# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisCd   import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/cd/{skill_name}
def creature_cd_add(creatureid,skill_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403
    if not request.is_json:
        msg = f'Missing JSON in request'
        logger.warning(msg)
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
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Cd add
    try:
        redis_cd = RedisCd(creature)
        # This returns True if the HASH is properly stored in Redis
        stored_cd = redis_cd.add(duration_base=duration,
                                 extra=extra,
                                 name=skill_name,
                                 source=source
                                 )
        creature_cds = redis_cd.get_all()
    except Exception as e:
        msg = f'Cd Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if stored_cd and creature_cds:
            msg = f'Cd add OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"cds":  creature_cds,
                                        "creature": creature}}), 200
        else:
            msg = f'Cd add KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: DELETE /internal/creature/{creatureid}/cd/{skill_name}
def creature_cd_del(creatureid,skill_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Cd del
    try:
        redis_cd      = RedisCd(creature)
        deleted_cd    = redis_cd.destroy(skill_name)
        creature_cds  = redis_cd.get_all()
    except Exception as e:
        msg = f'Cd Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if deleted_cd:
            msg = f'Cd del OK (creatureid:{creature.id},skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"cds":  creature_cds,
                                        "creature": creature}}), 200
        else:
            msg = f'Cd del KO - Failed (creatureid:{creature.id},skill_name:{skill_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/cd/{skill_name}
def creature_cd_get_one(creatureid,skill_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Cd get
    try:
        redis_cd    = RedisCd(creature)
        creature_cd = redis_cd.get(skill_name)
    except Exception as e:
        msg = f'Cd Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if creature_cd is False:
            msg = f'Cd get KO - Cd Not Found (creatureid:{creature.id},skill_name:{skill_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        elif creature_cd:
            msg = f'Cd get OK (creatureid:{creature.id},skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"cd":   creature_cd,
                                        "creature": creature}}), 200
        else:
            msg = f'Cd get KO - Failed (creatureid:{creature.id},skill_name:{skill_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/cds
def creature_cd_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # CDs get
    try:
        redis_cd      = RedisCd(creature)
        creature_cds  = redis_cd.get_all()
    except Exception as e:
        msg = f'CDs Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if isinstance(creature_cds, list):
            msg = f'CDs get OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"cds":  creature_cds,
                                        "creature": creature}}), 200
        else:
            msg = f'CDs get KO - Failed (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
