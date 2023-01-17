# -*- coding: utf8 -*-

import json
import requests

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect   import RedisEffect
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisStatus   import RedisStatus

from variables                  import RESOLVER_URL
from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

#
# Routes /mypc/{creatureuuid}/action/resolver/*
#


# API: POST /mypc/{creatureuuid}/action/resolver/skill/{skill_name}
@jwt_required()
def action_resolver_skill(creatureuuid, skill_name):
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

    # To use in RediSearch
    instance = Creature.instance.replace('-', ' ')

    try:
        bearer = Creature.id.replace('-', ' ')
        Cds = RedisCd().search(
                query=f'(@bearer:{bearer}) & (@name:{skill_name})'
                )
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
        if len(Cds) > 0:
            # The skill was already used, and still on CD
            msg = f'{h} Skill already on CD (skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": Cds._asdict,
                }
            ), 200

    try:
        Effects = RedisEffect().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Statuses = RedisStatus().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Cds = RedisCd().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(Creature)
    except Exception as e:
        msg = f'{h} RedisPa Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Instance = RedisInstance().get(Creature.instance)
        map      = Instance.map
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
        fightEventname     = request.json.get('name', None)
        fightEventtype     = request.json.get('type', None)
        fightEventactor    = request.json.get('actor', None)
        fightEventparams   = request.json.get('params', None)

        instance = Instance.id.replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@instance:{instance}')
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

    # Everythins if fine, we can build the payload
    # Supposedly got all infos
    payload = {
        "context": {
            "map": map,
            "instance": Creature.instance,
            "creatures": Creatures,
            "effects": Effects._asdict,
            "status": Statuses._asdict,
            "cd": Cds._asdict,
            "pa": creature_pa._asdict()
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
        response  = requests.post(f'{RESOLVER_URL}/', json=payload)
    except Exception as e:
        msg = f'{h} Resolver Query KO (skill_name:{skill_name}) [{e}]'
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
            action_type='skill',
            action_text=f'Used a Skill ({skill_name})',
            action_ttl=30 * 86400
            )
        msg = f'{h} Resolver Query OK (creatureuuid:{Creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {"resolver": json.loads(response.text),
                            "internal": payload},
            }
        ), 200


# API: POST /mypc/{creatureuuid}/action/resolver/move
@jwt_required()
def action_resolver_move(creatureuuid):
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

    # To use in RediSearch
    instance = Creature.instance.replace('-', ' ')

    try:
        Effects = RedisEffect().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Statuses = RedisStatus().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Cds = RedisCd().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(Creature)
    except Exception as e:
        msg = f'{h} RedisPa Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Instance = RedisInstance().get(Creature.instance)
        map      = Instance.map
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
        fightEventname     = request.json.get('name', None)
        fightEventtype     = request.json.get('type', None)
        fightEventactor    = request.json.get('actor', None)
        fightEventparams   = request.json.get('params', None)

        instance = Instance.id.replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@instance:{instance}')
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
            "creatures": Creatures,
            "effects": Effects._asdict,
            "status": Statuses._asdict,
            "cd": Cds._asdict,
            "pa": creature_pa._asdict()
        },
        "fightEvent": {
            "name": fightEventname,
            "type": fightEventtype,
            "actor": fightEventactor,
            "params": fightEventparams
        }
    }

    try:
        response  = requests.post(f'{RESOLVER_URL}/', json=payload)
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
                "payload": {"resolver": json.loads(response.text),
                            "internal": payload},
            }
        ), 200


# API: POST /mypc/{creatureuuid}/action/resolver/context
@jwt_required()
def action_resolver_context(creatureuuid):
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

    # To use in RediSearch
    instance = Creature.instance.replace('-', ' ')

    try:
        Statuses = RedisStatus().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Cds = RedisCd().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Effects = RedisEffect().search(query=f'@instance:{instance}')
    except Exception as e:
        msg = f'{h} RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(Creature)
    except Exception as e:
        msg = f'{h} RedisPa Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Instance = RedisInstance().get(Creature.instance)
        map      = Instance.map
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
        fightEventname     = request.json.get('name', None)
        fightEventtype     = request.json.get('type', None)
        fightEventactor    = request.json.get('actor', None)
        fightEventparams   = request.json.get('params', None)

        instance = Instance.id.replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@instance:{instance}')
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
            "creatures": Creatures,
            "effects": Effects._asdict,
            "status": Statuses._asdict,
            "cd": Cds._asdict,
            "pa": creature_pa._asdict()
        },
        "fightEvent": {
            "name": fightEventname,
            "type": fightEventtype,
            "actor": fightEventactor,
            "params": fightEventparams
        }
    }

    msg = f'{h} Context Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {"resolver": None,
                        "internal": payload},
        }
    ), 200
