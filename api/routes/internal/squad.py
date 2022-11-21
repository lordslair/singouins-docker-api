# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSquad    import RedisSquad

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# API: GET /internal/squad/{squadid}
def internal_squad_get_one(squadid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    try:
        Squad = RedisSquad().get(squadid)
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
        if Squad:
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
        elif Squad is False:
            msg = f'[Squad.id:{squadid}] Squad Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'[Squad.id:{squadid}] Squad Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/squads
def internal_squad_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

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
