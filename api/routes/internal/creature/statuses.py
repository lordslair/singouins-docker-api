# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStatus   import RedisStatus

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    request_json_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/status/{status_name}
def creature_status_add(creatureid, status_name):
    request_internal_token_check(request)
    request_json_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

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

    # Status add
    try:
        redis_status = RedisStatus(Creature)
        # This returns True if the HASH is properly stored in Redis
        stored_status = redis_status.add(
            duration_base=duration,
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
            msg = f'{h} Status Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "statuses": creature_statuses,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} Status Query KO'
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
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    # Cd del
    try:
        redis_status      = RedisStatus(Creature)
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
                        "creature": Creature._asdict(),
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
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    # Cd get
    try:
        redis_status    = RedisStatus(Creature)
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
                        "creature": Creature._asdict(),
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
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    # Statuses get
    try:
        redis_status      = RedisStatus(Creature)
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
                        "creature": Creature._asdict(),
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
