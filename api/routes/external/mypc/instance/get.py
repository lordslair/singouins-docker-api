# -*- coding: utf8 -*-

from flask                               import jsonify
from flask_jwt_extended                  import (jwt_required,
                                                 get_jwt_identity)
from loguru                              import logger

from nosql.models.RedisCreature          import RedisCreature
from nosql.models.RedisInstance          import RedisInstance

from utils.routehelper          import (
    creature_check,
    )


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: GET /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>
@jwt_required()
def get(creatureuuid, instanceuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.instance is None:
        msg = f'{h} Not in an Instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if Creature.instance != str(instanceuuid):
        msg = f'{h} Not in Instance({instanceuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": Creature.as_dict(),
            }
        ), 200

    # Check if the instance exists
    try:
        Instance = RedisInstance(instanceuuid=Creature.instance)
    except Exception as e:
        msg = f'{h} Instance({instanceuuid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Instance.id:
            msg = f'{h} Instance({Instance.id}) Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Instance.as_dict(),
                }
            ), 200
        else:
            msg = f'{h} Instance({Instance.id}) Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
