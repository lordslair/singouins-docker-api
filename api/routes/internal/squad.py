# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSquad    import RedisSquad

from utils.routehelper          import (
    request_internal_token_check,
    )

#
# Routes /internal
#


# API: GET /internal/squad/{squadid}
def internal_squad_get_one(squadid):
    request_internal_token_check(request)

    try:
        Squad = RedisSquad().get(squadid)
    except Exception as e:
        msg = f'[Squad.id:{squadid}] Squad Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Squad is False or Squad is None:
            msg = f'[Squad.id:{squadid}] Squad Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 404

    try:
        squad = Squad.id.replace('-', ' ')
        SquadMembers = RedisCreature().search(
            f"(@squad:{squad}) & (@squad_rank:-Pending)"
            )
        SquadPending = RedisCreature().search(
            f"(@squad:{squad}) & (@squad_rank:Pending)"
            )
    except Exception as e:
        msg = f'[Squad.id:{squadid}] Squad Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'[Squad.id:{Squad.id}] Squad Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "members": SquadMembers,
                    "pending": SquadPending,
                    "squad": Squad._asdict(),
                    }
            }
        ), 200


# API: GET /internal/squads
def internal_squad_get_all():
    request_internal_token_check(request)

    try:
        Squads = RedisSquad().search(query='-(@instance:None)')
    except Exception as e:
        msg = f'[Squad.id:None] Squads Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = '[Squad.id:None] Squads Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Squads,
            }
        ), 200
