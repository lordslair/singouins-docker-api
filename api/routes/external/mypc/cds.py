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
# Routes /mypc/{pcid}/cds
#


# API: GET /mypc/{pcid}/cds
@jwt_required()
def cds_get(pcid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    try:
        creature_cd  = RedisCd(Creature)
        creature_cds = creature_cd.get_all()
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
                "payload": {"cds": creature_cds,
                            "creature": Creature._asdict()},
            }
        ), 200
