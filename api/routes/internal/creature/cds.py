# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisCreature import RedisCreature

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/cd/{skill_name}
def creature_cd_add(creatureid, skill_name):
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

    # Cd add
    try:
        redis_cd = RedisCd(Creature)
        # This returns True if the HASH is properly stored in Redis
        stored_cd = redis_cd.add(
            duration_base=duration,
            extra=extra,
            name=skill_name,
            source=source
            )
        creature_cds = redis_cd.get_all()
    except Exception as e:
        msg = f'{h} CD Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if stored_cd and creature_cds:
            msg = f'{h} CD Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "cds": creature_cds,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} CD Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: DELETE /internal/creature/{creatureid}/cd/{skill_name}
def creature_cd_del(creatureid, skill_name):
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

    # Cd del
    try:
        redis_cd      = RedisCd(Creature)
        deleted_cd    = redis_cd.destroy(skill_name)
        creature_cds  = redis_cd.get_all()
    except Exception as e:
        msg = f'{h} CD Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if deleted_cd:
            msg = f'{h} CD Query OK (skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "cds": creature_cds,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} CD Query KO - Failed (skill_name:{skill_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/cd/{skill_name}
def creature_cd_get_one(creatureid, skill_name):
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

    # Cd get
    try:
        redis_cd    = RedisCd(Creature)
        creature_cd = redis_cd.get(skill_name)
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
        if creature_cd is False:
            msg = f'{h} CD Query KO - NotFound (skill_name:{skill_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        elif creature_cd:
            msg = f'{h} CD Query OK (skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "cd": creature_cd,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} CD Query KO - Failed (skill_name:{skill_name})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/cds
def creature_cd_get_all(creatureid):
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

    # CDs get
    try:
        redis_cd      = RedisCd(Creature)
        creature_cds  = redis_cd.get_all()
    except Exception as e:
        msg = f'{h} CDs Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if isinstance(creature_cds, list):
            msg = f'{h} CDs Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "cds": creature_cds,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} CDs Query KO - Failed'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
