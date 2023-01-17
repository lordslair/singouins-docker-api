# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect   import RedisEffect
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisStatus   import RedisStatus

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/context
def creature_context_get(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature)

    try:
        creatures_effect  = RedisEffect(Creature)
        creatures_effects = creatures_effect.get_all_instance()
    except Exception as e:
        msg = f'{h} RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_status   = RedisStatus(Creature)
        creatures_statuses = creatures_status.get_all_instance()
    except Exception as e:
        msg = f'{h} RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_cd  = RedisCd(Creature)
        creatures_cds = creatures_cd.get_all_instance()
    except Exception as e:
        msg = f'{h} RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(Creature)
    except Exception as e:
        msg = f'{h} RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Instance = RedisInstance().get(Creature.instance)
        map      = Instance.map
    except Exception as e:
        msg = f'{h} RedisInstance Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        instance = Instance.id.replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} Creature Query Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Supposedly got all infos
    msg = f'{h} Context Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "map": map,
                "instance": Creature.instance,
                "creatures": Creatures,
                "effects": creatures_effects,
                "status": creatures_statuses,
                "cd": creatures_cds,
                "pa": creature_pa._asdict(),
                },
        }
    ), 200
