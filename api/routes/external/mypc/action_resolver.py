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
from nosql.models.RedisUser     import RedisUser

from variables                  import RESOLVER_URL
from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

#
# Routes /mypc/{pcid}/action/resolver/*
#


# API: POST /mypc/{pcid}/action/resolver/skill/{skill_name}
@jwt_required()
def action_resolver_skill(pcid, skill_name):
    request_json_check(request)

    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

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
        redis_cd    = RedisStatus(Creature)
        creature_cd = redis_cd.get(skill_name)
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
        if creature_cd:
            # The skill was already used, and still on CD
            msg = f'{h} Skill already on CD (skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": creature_cd,
                }
            ), 200

    try:
        creatures_effect  = RedisEffect(Creature)
        creatures_effects = creatures_effect.get_all_instance()
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
        creatures_status   = RedisStatus(Creature)
        creatures_statuses = creatures_status.get_all_instance()
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
        creatures_cd  = RedisCd(Creature)
        creatures_cds = creatures_cd.get_all_instance()
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
            "effects": creatures_effects,
            "status": creatures_statuses,
            "cd": creatures_cds,
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
        RedisEvent(Creature).add(Creature.id,
                                 None,
                                 'skill',
                                 f'Used a Skill ({skill_name})',
                                 30 * 86400)
        msg = f'{h} Resolver Query OK (pcid:{Creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {"resolver": json.loads(response.text),
                            "internal": payload},
            }
        ), 200


# API: POST /mypc/{pcid}/action/resolver/move
@jwt_required()
def action_resolver_move(pcid):
    request_json_check(request)

    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

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
        creatures_effect  = RedisEffect(Creature)
        creatures_effects = creatures_effect.get_all_instance()
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
        creatures_status   = RedisStatus(Creature)
        creatures_statuses = creatures_status.get_all_instance()
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
        creatures_cd  = RedisCd(Creature)
        creatures_cds = creatures_cd.get_all_instance()
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
            "effects": creatures_effects,
            "status": creatures_statuses,
            "cd": creatures_cds,
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
        RedisEvent(Creature).add(Creature.id,
                                 None,
                                 'action',
                                 'Moved',
                                 30 * 86400)
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


# API: POST /mypc/{pcid}/action/resolver/context
@jwt_required()
def action_resolver_context(pcid):
    request_json_check(request)

    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

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
        creatures_effect  = RedisEffect(Creature)
        creatures_effects = creatures_effect.get_all_instance()
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
        creatures_status   = RedisStatus(Creature)
        creatures_statuses = creatures_status.get_all_instance()
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
        creatures_cd  = RedisCd(Creature)
        creatures_cds = creatures_cd.get_all_instance()
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
            "effects": creatures_effects,
            "status": creatures_statuses,
            "cd": creatures_cds,
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
