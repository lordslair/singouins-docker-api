# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from utils.decorators import check_creature_exists
from utils.redis import get_pa


#
# Routes /mypc/<uuid:creatureuuid>/pa/*
#
# API: GET /mypc/<uuid:creatureuuid>/pa
@jwt_required()
# Custom decorators
@check_creature_exists
def pa_get(creatureuuid):
    try:
        msg = f'{g.h} PA Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": get_pa(creatureuuid=g.Creature.id),
            }
        ), 200
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
