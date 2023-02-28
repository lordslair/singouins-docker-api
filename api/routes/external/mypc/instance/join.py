# -*- coding: utf8 -*-

from flask                               import jsonify
from flask_jwt_extended                  import (jwt_required,
                                                 get_jwt_identity)
from loguru                              import logger

from nosql.queue                         import yqueue_put
from nosql.models.RedisCreature          import RedisCreature
from nosql.models.RedisSearch            import RedisSearch

from utils.routehelper          import (
    creature_check,
    )

from variables                           import YQ_DISCORD


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: POST /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>/join
@jwt_required()
def join(creatureuuid, instanceuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.instance is not None:
        msg = f'{h} in in Instance({Creature.instance})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Check if the Instance exists
    try:
        Instances = RedisSearch().instance(
            query=(
                f"@id:{str(instanceuuid).replace('-', ' ')}"
                )
            )
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
        if len(Instances.results) == 0:
            msg = f'{h} Instance({instanceuuid}) Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.debug(f'{h} Instance({instanceuuid}) Query OK')
            Instance = Instances.results[0]

    # We add the Creature into the instance
    try:
        Creature.instance = Instance.id
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
        # We put the info in queue for Discord
        scopes = []
        if Creature.korp is not None:
            scopes.append(f'Korp-{Creature.korp}')
        if Creature.squad is not None:
            scopes.append(f'Squad-{Creature.squad}')
        for scope in scopes:
            # Discord Queue
            yqueue_put(
                YQ_DISCORD,
                {
                    "ciphered": False,
                    "payload": (
                        f':map: **[{Creature.id}] {Creature.name}** '
                        f'joined an Instance ({Instance.id})'
                        ),
                    "embed": None,
                    "scope": scope,
                    }
                )
        # Everything went well
        msg = f'{h} Instance({instanceuuid}) Join OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature.as_dict(),
            }
        ), 200
