# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisEffect   import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_add(creatureid,effect_name):
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
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Effect add
    try:
        redis_effect = RedisEffect(creature)

        redis_effect.duration_base = duration
        redis_effect.name          = effect_name
        redis_effect.source        = creature.id
        redis_effect.extra         = extra

        # This returns True if the HASH is properly stored in Redis
        stored_effect    = redis_effect.store()
        creature_effects = redis_effect.get_all()
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if stored_effect and creature_effects:
            msg = f'Effect add OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"effects":  creature_effects,
                                        "creature": creature}}), 200
        else:
            msg = f'Effect add KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

# API: DELETE /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_del(creatureid,effect_name):
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

    # Effect del
    try:
        redis_effect      = RedisEffect(creature)
        deleted_effect    = redis_effect.destroy(effect_name)
        creature_effects  = redis_effect.get_all()
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if deleted_effect:
            msg = f'Effect del OK (creatureid:{creature.id},effect_name:{effect_name})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"effects":  creature_effects,
                                        "creature": creature}}), 200
        else:
            msg = f'Effect del KO - Failed (creatureid:{creature.id},effect_name:{effect_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_get_one(creatureid,effect_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Effect get
    try:
        redis_effect    = RedisEffect(creature)
        creature_effect = redis_effect.get(effect_name)
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if creature_effect is False:
            msg = f'Effect get KO - Effect Not Found (creatureid:{creature.id},effect_name:{effect_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        elif creature_effect:
            msg = f'Effect get OK (creatureid:{creature.id},effect_name:{effect_name})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"effect":   creature_effect.dict,
                                        "creature": creature}}), 200
        else:
            msg = f'Effect get KO - Failed (creatureid:{creature.id},effect_name:{effect_name})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200

# API: GET /internal/creature/{creatureid}/effects
def creature_effect_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200

    # Effects get
    try:
        redis_effect      = RedisEffect(creature)
        creature_effects  = redis_effect.get_all()
    except Exception as e:
        msg = f'Effects Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if isinstance(creature_effects, list):
            msg = f'Effects get OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": {"effects":  creature_effects,
                                        "creature": creature}}), 200
        else:
            msg = f'Effects get KO - Failed (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
