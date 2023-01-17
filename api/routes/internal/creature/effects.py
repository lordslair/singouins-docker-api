# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect   import RedisEffect

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    request_json_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/effect/{effect_name}
def creature_effect_add(creatureid, effect_name):
    request_internal_token_check(request)
    request_json_check(request)

    Creature = RedisCreature(creatureuuid=creatureid)
    h = creature_check(Creature)

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
                        "creature": Creature.as_dict(),
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
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=creatureid)
    h = creature_check(Creature)

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
                        "creature": Creature.as_dict(),
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
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=creatureid)
    h = creature_check(Creature)

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
                        "creature": Creature.as_dict(),
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
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=creatureid)
    h = creature_check(Creature)

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
                        "creature": Creature.as_dict(),
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
