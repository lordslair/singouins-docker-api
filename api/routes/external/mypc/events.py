# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch

from utils.routehelper          import (
    creature_check,
    )


#
# Routes /mypc/<uuid:creatureuuid>/event/*
#
# API: GET /mypc/<uuid:creatureuuid>/event
@jwt_required()
def mypc_event_get_all(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Events = RedisSearch(maxpaging=100).event(
            query=(
                f"(@src:{Creature.id.replace('-', ' ')}) | "
                f"(@dst:{Creature.id.replace('-', ' ')})"
                ),
            )
    except Exception as e:
        msg = f'{h} Event Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Event Query OK'
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
