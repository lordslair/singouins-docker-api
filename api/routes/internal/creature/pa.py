# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get

from nosql.models.RedisPa       import RedisPa

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/pa
def creature_pa_get(creatureid):
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
        creature_pa = RedisPa(creature)
    except Exception as e:
        msg = f'{h} PA Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_pa:
            msg = f'{h} PA Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "pa": creature_pa._asdict(),
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} PA Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: PUT /internal/creature/{creatureid}/pa/consume/{redpa}/{bluepa}
def creature_pa_consume(creatureid, redpa, bluepa):
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

    if redpa > 16 or bluepa > 8:
        msg = (f'{h} Cannot consume more than max PA '
               f'(redpa:{redpa},bluepa:{bluepa})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if redpa < 0 or bluepa < 0:
        msg = f'{h} Cannot consume PA < 0  (redpa:{redpa},bluepa:{bluepa})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    creature_pa = RedisPa(creature)
    if redpa > creature_pa.redpa or bluepa > creature_pa.bluepa:
        msg = (f'{h} Cannot consume that amount of PA '
               f'(redpa:{redpa},bluepa:{bluepa})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        ret = creature_pa.consume(redpa=redpa, bluepa=bluepa)
    except Exception as e:
        msg = f'{h} PA Query KO (redpa:{redpa},bluepa:{bluepa}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if ret:
            msg = f'{h} PA Query OK (redpa:{redpa},bluepa:{bluepa})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "pa": creature_pa._asdict(),
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} PA Query KO (redpa:{redpa},bluepa:{bluepa})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /internal/creature/{creatureid}/pa/reset
def creature_pa_reset(creatureid):
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
        creature_pa = RedisPa(creature)
        ret         = creature_pa.reset()
    except Exception as e:
        msg = f'{h} PA Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if ret:
            msg = f'{h} PA Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "pa": creature_pa._asdict(),
                        "creature": creature,
                        },
                }
            ), 200
        else:
            msg = f'{h} PA Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
