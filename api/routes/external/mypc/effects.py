# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect   import RedisEffect
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{creatureuuid}/effects
#


# API: GET /mypc/{creatureuuid}/effects
@jwt_required()
def effects_get(creatureuuid):
    User = RedisUser(get_jwt_identity())
    Creature = RedisCreature().get(creatureuuid)
    h = creature_check(Creature, User)

    try:
        bearer = Creature.id.replace('-', ' ')
        Effects = RedisEffect(Creature).search(query=f'@bearer:{bearer}')
    except Exception as e:
        msg = f'{h} Effects Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Effects Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "effects": Effects._asdict,
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
