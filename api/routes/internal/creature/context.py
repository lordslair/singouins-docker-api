# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from variables                  import API_INTERNAL_TOKEN

from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect   import RedisEffect
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisStatus   import RedisStatus

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/context
def creature_context_get(creatureid):
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
