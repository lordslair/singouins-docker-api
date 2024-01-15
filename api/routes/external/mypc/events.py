# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisSearch   import RedisSearch

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/event/*
#
# API: GET /mypc/<uuid:creatureuuid>/event
@jwt_required()
# Custom decorators
@check_creature_exists
def mypc_event_get_all(creatureuuid):
    try:
        Events = RedisSearch(maxpaging=100).event(
            query=(
                f"(@src:{g.Creature.id.replace('-', ' ')}) | "
                f"(@dst:{g.Creature.id.replace('-', ' ')})"
                ),
            )
    except Exception as e:
        msg = f'{g.h} Event Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Event Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [
                    Event.as_dict() for Event in Events.results
                    ],
            }
        ), 200
