# -*- coding: utf8 -*-

import json
import requests

from flask                      import g, jsonify, request
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from mongo.models.Creature import CreatureDocument

from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisEffect   import RedisEffect
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisStatus   import RedisStatus

from variables                  import RESOLVER_URL
from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_is_json,
    )


#
# Routes /mypc/{creatureuuid}/action/resolver/*
#
# API: POST /mypc/{creatureuuid}/action/resolver/skill/{skill_name}
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
@check_creature_in_instance
def skill(creatureuuid, skill_name):
    try:
        Cds = RedisCd().search(
                query=(
                    f"(@bearer:{g.Creature.id.replace('-', ' ')})"
                    f"& (@name:{skill_name})"
                    )
                )
    except Exception as e:
        msg = f'{g.h} CDs Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if len(Cds) > 0:
            # The skill was already used, and still on CD
            msg = f'{g.h} Skill already on CD (skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": Cds._asdict,
                }
            ), 200

    try:
        Effects = RedisEffect().search(
            query=f"@instance:{g.Instance.id.replace('-', ' ')}"
            )
        Statuses = RedisStatus().search(
            query=f"@instance:{g.Instance.id.replace('-', ' ')}"
            )
        Cds = RedisCd().search(
            query=f"@instance:{g.Instance.id.replace('-', ' ')}"
            )
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

        Creatures = CreatureDocument.objects(instance=g.Instance.id)
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

    # Everythins if fine, we can build the payload
    # Supposedly got all infos
    payload = {
        "context": {
            "map": g.Instance.map,
            "instance": g.Instance.id,
            "creatures": [Creature.to_mongo() for Creature in Creatures],
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
        logger.trace(payload)
        response = requests.post(f'{RESOLVER_URL}/', json=payload)
    except Exception as e:
        msg = f'{g.h} Resolver Query KO (skill_name:{skill_name}) [{e}]'
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
            action_src=g.Creature.id,
            action_dst=None,
            action_type='skill',
            action_text=f'Used a Skill ({skill_name})',
            action_ttl=30 * 86400
            )
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
