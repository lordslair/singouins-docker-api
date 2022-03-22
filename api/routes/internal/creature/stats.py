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
            msg = f'Creature Query KO - Not Found (creatureid:{creature.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        # We check if we have the data in redis
        cached_stats = RedisStats(creature).as_dict()
        if cached_stats:
            # Data was in Redis, so we return it
            creature_stats = cached_stats
        else:
            # Data was not in Redis, so we compute it
            generated_stats = RedisStats(creature).refresh().dict
            if generated_stats:
                # Data was computed, so we return it
                creature_stats = generated_stats
            else:
                msg = f'Stats computation KO (pcid:{pc.id})'
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
                        "payload": {"stats":    creature_stats,
                                    "creature": creature}}), 200
