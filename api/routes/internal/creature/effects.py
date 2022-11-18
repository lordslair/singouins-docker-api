# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect   import RedisEffect

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_add(creatureid, effect_name):
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = f'{h} Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    duration    = request.json.get('duration')
    extra       = request.json.get('extra')
    source      = request.json.get('source')

    if not isinstance(duration, int):
        msg = f'{h} Duration should be an INT (duration:{duration})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(source, int):
        msg = f'{h} Source should be an INT (source:{source})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Effect add
    try:
        redis_effect = RedisEffect(Creature)
        # This returns True if the HASH is properly stored in Redis
        stored_effect = redis_effect.add(
            duration_base=duration,
            extra=extra,
            name=effect_name,
            source=source
            )
        creature_effects = redis_effect.get_all()
    except Exception as e:
        msg = f'{h} Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if stored_effect and creature_effects:
            msg = f'{h} Effect Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "effects": creature_effects,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} Effect Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: DELETE /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_del(creatureid, effect_name):
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Effect del
    try:
        redis_effect      = RedisEffect(Creature)
        deleted_effect    = redis_effect.destroy(effect_name)
        creature_effects  = redis_effect.get_all()
    except Exception as e:
        msg = f'{h} Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if deleted_effect:
            msg = f'{h} Effect Query OK (effect_name:{effect_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "effects": creature_effects,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} Effect Query KO - Failed (effect_name:{effect_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_get_one(creatureid, effect_name):
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Effect get
    try:
        redis_effect    = RedisEffect(Creature)
        creature_effect = redis_effect.get(effect_name)
    except Exception as e:
        msg = f'Effect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_effect is False:
            msg = f'{h} Effect Query KO - NotFound (effect_name:{effect_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        elif creature_effect:
            msg = f'{h} Effect Query OK (effect_name:{effect_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "effect": creature_effect,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} Effect Query KO - Failed (effect_name:{effect_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/effects
def creature_effect_get_all(creatureid):
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Effects get
    try:
        redis_effect      = RedisEffect(Creature)
        creature_effects  = redis_effect.get_all()
    except Exception as e:
        msg = f'{h} Effects Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if isinstance(creature_effects, list):
            msg = f'{h} Effects Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "effects": creature_effects,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} Effects Query KO - Failed'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
