# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisPa   import RedisPa

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/pa/*
#
# API: GET /mypc/<uuid:creatureuuid>/pa
@jwt_required()
# Custom decorators
@check_creature_exists
def pa_get(creatureuuid):
    try:
        Pa = RedisPa(creatureuuid=creatureuuid)
    except Exception as e:
        msg = f'{g.h} PA Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} PA Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Pa.as_dict(),
            }
        ), 200
