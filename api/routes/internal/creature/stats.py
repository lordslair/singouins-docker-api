# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisStats    import *

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: GET /internal/creature/{creatureid}/stats
def creature_stats(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    try:
        creature = fn_creature_get(None,creatureid)[3]
    except Exception as e:
        msg = f'Creature Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if not creature:
            msg = f'Creature Query KO - Not Found (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        # We check if we have the data in redis
        creature_stats = RedisStats(creature)
        if creature_stats:
            logger.trace(f'creature_stats:{creature_stats.__dict__}')
            pass
        else:
            msg = f'Stats computation KO (creature.id:{creature.id})'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
    except Exception as e:
        msg = f'Stats Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Stats Query OK (creatureid:{creature.id})',
                        "payload": {"stats":    creature_stats.dict,
                                    "creature": creature}}), 200

# API: PUT /internal/creature/{creatureid}/stats/hp/{operation}/{count}
def creature_stats_hp_modify(creatureid,operation,count):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warn(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    if not isinstance(count, int):
        return jsonify({"success": False,
                        "msg": f'Count should be an INT (count:{count})',
                        "payload": None}), 200
    if operation not in ['add','consume']:
        return jsonify({"success": False,
                        "msg": f"Operation should be in ['add','consume'] (operation:{operation})",
                        "payload": None}), 200

    # Pre-flight checks
    try:
        creature = fn_creature_get(None,creatureid)[3]
    except Exception as e:
        msg = f'Creature Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if not creature:
            msg = f'Creature Query KO - Not Found (creatureid:{creatureid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        creature_stats  = RedisStats(creature)
        # We store back the modified value
        if operation == 'consume':
            creature_stats.hp = int(creature_stats.hp) - count
        elif operation == 'add':
            creature_stats.hp = int(creature_stats.hp) + count
        else:
            pass
        # We store updated stats
        storage = creature_stats.store()

    except Exception as e:
        msg = f'Stats Query KO (creatureid:{creature.id},operation:{operation},count:{count}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if storage:
            creature_stats  = RedisStats(creature)
            return jsonify({"success": True,
                            "msg": f'Stats Query OK (creatureid:{creature.id})',
                            "payload": {"stats":    creature_stats.dict,
                                        "creature": creature}}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'Stats Query KO - RedisStats store() Failed',
                            "payload": None}), 200
