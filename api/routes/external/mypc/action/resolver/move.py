# -*- coding: utf8 -*-

import json
import requests

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisSearch   import RedisSearch

from variables                  import RESOLVER_URL
from utils.routehelper          import (
    creature_check,
    request_json_check,
    )


#
# Routes /mypc/<uuid:creatureuuid>/action/resolver/*
#
# API: POST /mypc/<uuid:creatureuuid>/action/resolver/move
@jwt_required()
def move(creatureuuid):
    request_json_check(request)

    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.instance is None:
        msg = f'{h} Creature not in an instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Statuses = RedisSearch().status(
            query=f"@instance:{Creature.instance.replace('-', ' ')}"
            )
        Cds = RedisSearch().cd(
            query=f"@instance:{Creature.instance.replace('-', ' ')}"
            )
        Effects = RedisSearch().effect(
            query=f"@instance:{Creature.instance.replace('-', ' ')}"
            )
        Creatures = RedisSearch().creature(
            query=f"@instance:{Creature.instance.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} RedisSearch Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Instance = RedisInstance(instanceuuid=Creature.instance)
        map = Instance.map
    except Exception as e:
        msg = f'{h} RedisInstance Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fightEventname = request.json.get('name', None)
        fightEventtype = request.json.get('type', None)
        fightEventactor = request.json.get('actor', None)
        fightEventparams = request.json.get('params', None)
    except Exception as e:
        msg = f'{h} ResolverInfo Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Supposedly got all infos
    payload = {
        "context": {
            "map": map,
            "instance": Creature.instance,
            "creatures": [
                Creature.as_dict() for Creature in Creatures.results
                ],
            "effects": [
                Effect.as_dict() for Effect in Effects.results
                ],
            "status": [
                Status.as_dict() for Status in Statuses.results
                ],
            "cd": [
                Cd.as_dict() for Cd in Cds.results
                ],
        },
        "fightEvent": {
            "name": fightEventname,
            "type": fightEventtype,
            "actor": fightEventactor,
            "params": fightEventparams
        }
    }

    try:
        response = requests.post(f'{RESOLVER_URL}/', json=payload)
    except Exception as e:
        msg = f'{h} Resolver Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # We create the Creature Event
        RedisEvent().new(
            action_src=Creature.id,
            action_dst=None,
            action_type='action/move',
            action_text='Moved',
            action_ttl=30 * 86400
            )
        msg = f'{h} Resolver Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "resolver": json.loads(response.text),
                    "internal": payload,
                    },
            }
        ), 200
