# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisStats    import RedisStats

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/stats
def creature_stats(creatureid):
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

    try:
        # We check if we have the data in redis
        creature_stats = RedisStats(creature)
        if creature_stats:
            logger.trace(f'creature_stats:{creature_stats.__dict__}')
            pass
        else:
            msg = f'{h} Stats computation KO'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
    except Exception as e:
        msg = f'{h} Stats Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Stats Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "stats": creature_stats._asdict(),
                    "creature": creature,
                    },
            }
        ), 200


# API: PUT /internal/creature/{creatureid}/stats/hp/{operation}/{count}
def creature_stats_hp_modify(creatureid, operation, count):
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

    if not isinstance(count, int):
        msg = f'Count should be an INT (count:{count})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if operation not in ['add', 'consume']:
        msg = (f"Operation should be in "
               f"['add','consume'] (operation:{operation})")
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

    try:
        creature_stats  = RedisStats(creature)
        # We store back the modified value
        if operation == 'consume':
            creature_stats.hp -= count
        elif operation == 'add':
            creature_stats.hp += count
        else:
            pass
    except Exception as e:
        msg = f'{h} Stats Query KO (operation:{operation},count:{count}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        creature_stats  = RedisStats(creature)
        msg = f'{h} Stats Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "stats": creature_stats._asdict(),
                    "creature": creature,
                    },
            }
        ), 200
