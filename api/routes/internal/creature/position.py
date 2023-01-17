# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

from variables                  import YQ_BROADCAST

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/position/{x}/{y}
def creature_position_set(creatureid, x, y):
    request_internal_token_check(request)

    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature)

    try:
        Creature.x = x
        Creature.y = y
    except Exception as e:
        msg = f'{h} Position Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Position Query OK'
        logger.debug(msg)

        # Now we send the WS messages
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": {
                    "id": Creature.id,
                    "x": Creature.x,
                    "y": Creature.y,
                    },
                "route": "mypc/{id1}/action/move",
                "scope": {
                    "id": None,
                    "scope": 'broadcast'
                    },
                }
            )

        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature.as_dict(),
            }
        ), 200
