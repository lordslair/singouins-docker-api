# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisSearch   import RedisSearch

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/cds
#
# API: GET /mypc/<uuid:creatureuuid>/cds
@jwt_required()
# Custom decorators
@check_creature_exists
def cds_get(creatureuuid):
    try:
        Cds = RedisSearch().cd(
            query=f"@bearer:{str(g.Creature.id).replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Cds Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Cds Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "cds": [Cd.as_dict() for Cd in Cds.results],
                    "creature": g.Creature.to_mongo(),
                    },
            }
        ), 200
