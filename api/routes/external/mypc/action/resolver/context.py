# -*- coding: utf8 -*-

import json

from bson import json_util
from flask import g, jsonify, request
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Creature import CreatureDocument

from nosql.models.RedisSearch import RedisSearch

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_is_json,
    check_user_exists,
    check_creature_owned,
    )


#
# Routes /mypc/<uuid:creatureuuid>/action/resolver/*
#
# API: POST /mypc/<uuid:creatureuuid>/action/resolver/context
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
@check_creature_in_instance
@check_user_exists
@check_creature_owned
def context(creatureuuid):
    try:
        instanceuuid = str(g.Creature.instance).replace('-', ' ')
        Statuses = RedisSearch().status(query=f"@instance:{instanceuuid}")
        Cds = RedisSearch().cd(query=f"@instance:{instanceuuid}")
        Effects = RedisSearch().effect(query=f"@instance:{instanceuuid}")

        Creatures = CreatureDocument.objects.filter(instance=g.Creature.instance)
    except Exception as e:
        msg = f'{g.h} RedisSearch Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    logger.success(request.json)

    try:
        fightEventname = request.json.get('name', None)
        fightEventtype = request.json.get('type', None)
        fightEventactor = request.json.get('actor', None)
        fightEventparams = request.json.get('params', None)
    except Exception as e:
        msg = f'{g.h} ResolverInfo Query KO [{e}]'
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
            "map": g.Instance.map,
            "instance": g.Instance.id,
            "creatures": [
                json.loads(json_util.dumps(Creature.to_mongo())) for Creature in Creatures
                ],
            "effects": [Effect.as_dict() for Effect in Effects.results],
            "status": [Status.as_dict() for Status in Statuses.results],
            "cd": [Cd.as_dict() for Cd in Cds.results],
        },
        "fightEvent": {
            "name": fightEventname,
            "type": fightEventtype,
            "actor": fightEventactor,
            "params": fightEventparams
        }
    }

    msg = f'{g.h} Context Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "resolver": None,
                "internal": payload,
                },
        }
    ), 200
