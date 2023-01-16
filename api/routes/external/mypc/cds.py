# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{creatureuuid}/cds
#


# API: GET /mypc/{creatureuuid}/cds
@jwt_required()
def cds_get(creatureuuid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(creatureuuid)
    h = creature_check(Creature, User)

    try:
        bearer = Creature.id.replace('-', ' ')
        Cds = RedisCd(Creature).search(query=f'@bearer:{bearer}')
    except Exception as e:
        msg = f'{h} CDs Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} CDs Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "cds": Cds._asdict,
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
