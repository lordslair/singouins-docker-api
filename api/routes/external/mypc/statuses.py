# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStatus   import RedisStatus
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{creatureuuid}/statuses
#


# API: GET /mypc/{creatureuuid}/statuses
@jwt_required()
def statuses_get(creatureuuid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(creatureuuid)
    h = creature_check(Creature, User)

    try:
        bearer = Creature.id.replace('-', ' ')
        Statuses = RedisStatus(Creature).search(query=f'@bearer:{bearer}')
    except Exception as e:
        msg = f'{h} Statuses Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Statuses Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "statuses": Statuses._asdict,
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
