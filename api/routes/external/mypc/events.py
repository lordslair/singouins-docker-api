# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{pcid}/event/*
#


# API: GET /mypc/{pcid}/event
@jwt_required()
def mypc_event_get_all(pcid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        action_src = Creature.id.replace('-', ' ')
        action_dst = Creature.id.replace('-', ' ')
        creature_events = RedisEvent().search(
            query=f'(@src:{action_src}) | (@dst:{action_dst})',
            maxpaging=100,
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
                "payload": creature_events._asdict,
            }
        ), 200
