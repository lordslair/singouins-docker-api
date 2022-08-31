# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_creatures import fn_creatures_in_instance

from variables                  import API_INTERNAL_TOKEN

from nosql.models.RedisPa       import *
from nosql.models.RedisEvent    import *
from nosql.models.RedisCd       import *
from nosql.models.RedisEffect   import *
from nosql.models.RedisInstance import *
from nosql.models.RedisStatus   import *

#
# Routes /internal
#
# /internal/creature/*
# API: GET /internal/creature/{creatureid}/context
def creature_context_get(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    try:
        creature = fn_creature_get(None,creatureid)[3]
    except Exception as e:
        msg = f'Creature Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if not creature:
            msg = f'Creature Query KO - Not Found (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200

    try:
        creatures_effect  = RedisEffect(creature)
        creatures_effects = creatures_effect.get_all_instance()
    except Exception as e:
        msg = f'RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    try:
        creatures_status   = RedisStatus(creature)
        creatures_statuses = creatures_status.get_all_instance()
    except Exception as e:
        msg = f'RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    try:
        creatures_cd  = RedisCd(creature)
        creatures_cds = creatures_cd.get_all_instance()
    except Exception as e:
        msg = f'RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    try:
        pas = RedisPa(creature).get()
    except Exception as e:
        msg = f'RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    try:
        instance = RedisInstance(creature = creature)
        map      = instance.map
    except Exception as e:
        msg = f'RedisInstance Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    try:
        creatures = fn_creatures_in_instance(creature.instance)
    except Exception as e:
        msg = f'Creature Query Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    # Supposedly got all infos
    payload = {
        "map": map,
        "instance": creature.instance,
        "creatures": creatures,
        "effects": creatures_effects,
        "status": creatures_statuses,
        "cd": creatures_cds,
        "pa": pas,
        }

    return jsonify({"success": True,
                    "msg": "Context Query OK",
                    "payload": payload}), 200
