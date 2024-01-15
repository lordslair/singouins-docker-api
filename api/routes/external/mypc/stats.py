# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisStats   import RedisStats

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/stats/*
#
# API: GET /mypc/<uuid:creatureuuid>/stats
@jwt_required()
# Custom decorators
@check_creature_exists
def stats_get(creatureuuid):
    try:
        Stats = RedisStats(creatureuuid=creatureuuid)
    except Exception as e:
        msg = f'{g.h} Stats Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Stats Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Stats.as_dict(),
            }
        ), 200
