# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisStatus   import RedisStatus

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/status/{status_name}
def creature_status_add(creatureid, status_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
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
        msg = f'Duration should be an INT (duration:{duration})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(source, int):
        msg = f'Source should be an INT (source:{source})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    # Cd add
    try:
        redis_status = RedisStatus(creature)
        # This returns True if the HASH is properly stored in Redis
        stored_status = redis_status.add(duration_base=duration,
                                         extra=extra,
                                         name=status_name,
                                         source=source
                                         )
        creature_statuses = redis_status.get_all()
    except Exception as e:
        msg = f'{h} Status Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if stored_status and creature_statuses:
            msg = f'{h} Status Query OK (creatureid:{creature.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "statuses": creature_statuses,
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Status Query KO (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: DELETE /internal/creature/{creatureid}/status/{status_name}
def creature_status_del(creatureid, status_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    # Cd del
    try:
        redis_status      = RedisStatus(creature)
        deleted_status    = redis_status.destroy(status_name)
        creature_statuses = redis_status.get_all()
    except Exception as e:
        msg = f'{h} Status Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if deleted_status:
            msg = f'{h} Status Query OK (status_name:{status_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "statuses": creature_statuses,
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Status Query KO - Failed (status_name:{status_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/status/{status_name}
def creature_status_get_one(creatureid, status_name):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    # Cd get
    try:
        redis_status    = RedisStatus(creature)
        creature_status = redis_status.get(status_name)
    except Exception as e:
        msg = f'Cd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_status is False:
            msg = f'{h} Status Query KO - NotFound (status_name:{status_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        elif creature_status:
            msg = f'{h} Status Query OK (status_name:{status_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "status": creature_status,
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Status Query KO - Failed (status_name:{status_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/statuses
def creature_status_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    # Statuses get
    try:
        redis_status      = RedisStatus(creature)
        creature_statuses = redis_status.get_all()
    except Exception as e:
        msg = f'{h} Statuses Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if isinstance(creature_statuses, list):
            msg = f'{h} Statuses Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "statuses": creature_statuses,
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} Statuses Query KO - Failed'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
