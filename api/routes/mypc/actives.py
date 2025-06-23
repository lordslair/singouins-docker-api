# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from utils.decorators import check_creature_exists
from utils.redis import r, str2typed

from variables import env_vars


#
# Routes /mypc/<uuid:creatureuuid>/actives/<string:actives_type>
#
# API: GET /mypc/<uuid:creatureuuid>/actives/<string:actives_type>
@jwt_required()
# Custom decorators
@check_creature_exists
def actives_get(creatureuuid, actives_type):
    if actives_type not in ['effects', 'statuses', 'cds']:
        msg = f'{g.h} Invalid actives type ({actives_type})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    try:
        # Get all keys matching the pattern
        rpath = f"{env_vars['API_ENV']}:{g.Creature.instance}:{actives_type}:{g.Creature.id}:*"
        keys = r.keys(rpath)

        if len(keys) == 0:
            logger.trace(f'{g.h} No {actives_type.capitalize()} in Redis')

        results = []
        # Fetch hash values and TTL for each key
        for key in keys:
            result = {}
            hashdict = r.hgetall(key)  # Fetch hash data

            for k, v in hashdict.items():
                result[k.decode()] = str2typed(v.decode())

            result['duration_left'] = r.ttl(key)  # Fetch TTL
            results.append(result)
    except Exception as e:
        msg = f'{g.h} {actives_type.capitalize()} Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} {actives_type.capitalize()} Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    f"{actives_type}": results,
                    "creature": g.Creature.to_mongo(),
                    },
            }
        ), 200
