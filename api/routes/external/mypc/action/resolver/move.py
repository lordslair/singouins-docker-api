# -*- coding: utf8 -*-

import json
import requests

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
    )

from variables import RESOLVER_URL


#
# Routes /mypc/<uuid:creatureuuid>/action/resolver/*
#
# API: POST /mypc/<uuid:creatureuuid>/action/resolver/move
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
@check_creature_in_instance
def move(creatureuuid):
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
            "instance": str(g.Instance.id),
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

    try:
        response = requests.post(f'{RESOLVER_URL}/', json=payload)
    except Exception as e:
        msg = f'{g.h} Resolver Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

        """# We create the Creature Event
        RedisEvent().new(
            action_src=g.Creature.id,
            action_dst=None,
            action_type='action/move',
            action_text='Moved',
            action_ttl=30 * 86400
            )"""
    if response:
        msg = f'{g.h} Resolver Query OK'
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
    else:
        msg = f'{g.h} Resolver Query KO'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
