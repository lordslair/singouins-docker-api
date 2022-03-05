# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity

from mysql.methods      import fn_creature_get,fn_user_get
from nosql              import *

#
# Routes /mypc/{pcid}/stats
#
# API: GET /mypc/{pcid}/stats
@jwt_required()
def stats_get(creatureid):
    creature = fn_creature_get(None,creatureid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200
    if creature.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                        "payload": None}), 409

    try:
        # We check if we have the data in redis
        cached_stats = stats.get_stats(creature)
        if cached_stats:
            # Data was in Redis, so we return it
            creature_stats = cached_stats
        else:
            # Data was not in Redis, so we compute it
            generated_stats = fn_creature_stats(pc)
            if generated_stats:
                # Data was computed, so we return it
                creature_stats = generated_stats
            else:
                # Data computation failed
                return (200,
                        False,
                        f'Stats computation KO (creatureid:{creature.id})',
                        None)
    except Exception as e:
        msg = f'Stats Query KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Stats Query OK (creatureid:{creature.id})',
                        "payload": creature_stats}), 200
