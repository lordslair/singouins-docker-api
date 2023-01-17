# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats    import RedisStats

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/stats
def creature_stats(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature)

    try:
        Stats = RedisStats(Creature)
    except Exception as e:
        msg = f'{h} Stats Query KO [{e}]'
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
                    "stats": Stats._asdict(),
                    "creature": Creature.as_dict(),
                    },
            }
        ), 200


# API: PUT /internal/creature/{creatureid}/stats/hp/{operation}/{count}
def creature_stats_hp_modify(creatureid, operation, count):
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature)

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

    try:
        Stats  = RedisStats(Creature)
        # We store back the modified value
        if operation == 'consume':
            Stats.hp -= count
        elif operation == 'add':
            Stats.hp += count
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
        msg = f'{h} Stats Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "stats": Stats._asdict(),
                    "creature": Creature.as_dict(),
                    },
            }
        ), 200
