# -*- coding: utf8 -*-

import json
import requests

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_creatures import fn_creatures_in_instance
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisCd       import RedisCd
from nosql.models.RedisEffect   import RedisEffect
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisStatus   import RedisStatus

from variables                  import RESOLVER_URL


#
# Routes /mypc/{pcid}/action/resolver/*
#
# API: POST /mypc/{pcid}/action/resolver/skill/{skill_name}
@jwt_required()
def action_resolver_skill(pcid, skill_name):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.instance is None:
        msg = f'Creature not in an instance (creature.id:{creature.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        redis_cd    = RedisStatus(creature)
        creature_cd = redis_cd.get(skill_name)
    except Exception as e:
        msg = f'CDs Query KO (pcid:{creature.id}) [{e}]'
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
            msg = (f'Skill already on CD '
                   f'(pcid:{creature.id},skill_name:{skill_name})')
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": creature_cd,
                }
            ), 200

    try:
        creatures_effect  = RedisEffect(creature)
        creatures_effects = creatures_effect.get_all_instance()
    except Exception as e:
        msg = f'RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_status   = RedisStatus(creature)
        creatures_statuses = creatures_status.get_all_instance()
    except Exception as e:
        msg = f'RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_cd  = RedisCd(creature)
        creatures_cds = creatures_cd.get_all_instance()
    except Exception as e:
        msg = f'RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(creature)
    except Exception as e:
        msg = f'RedisPa Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        instance = RedisInstance(creature=creature)
        map      = instance.map
    except Exception as e:
        msg = f'RedisInstance Query KO [{e}]'
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
        creatures          = fn_creatures_in_instance(creature.instance)
    except Exception as e:
        msg = f'ResolverInfo Query KO [{e}]'
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
            "instance": creature.instance,
            "creatures": creatures,
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
        msg = (f'Resolver Query KO '
               f'(pcid:{creature.id},skill_name:{skill_name}) [{e}]')
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
        RedisEvent(creature).add(creature.id,
                                 None,
                                 'skill',
                                 f'Used a Skill ({skill_name})',
                                 30 * 86400)
        msg = f'Resolver Query OK (pcid:{creature.id})'
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
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.instance is None:
        msg = f'Creature not in an instance (creature.id:{creature.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_effect  = RedisEffect(creature)
        creatures_effects = creatures_effect.get_all_instance()
    except Exception as e:
        msg = f'RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_status   = RedisStatus(creature)
        creatures_statuses = creatures_status.get_all_instance()
    except Exception as e:
        msg = f'RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_cd  = RedisCd(creature)
        creatures_cds = creatures_cd.get_all_instance()
    except Exception as e:
        msg = f'RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(creature)
    except Exception as e:
        msg = f'RedisPa Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        instance = RedisInstance(creature=creature)
        map      = instance.map
    except Exception as e:
        msg = f'RedisInstance Query KO [{e}]'
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
        creatures          = fn_creatures_in_instance(creature.instance)
    except Exception as e:
        msg = f'ResolverInfo Query KO [{e}]'
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
            "instance": creature.instance,
            "creatures": creatures,
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
        msg = f'Resolver Query KO - Failed (pcid:{creature.id}) [{e}]'
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
        RedisEvent(creature).add(creature.id,
                                 None,
                                 'action',
                                 'Moved',
                                 30 * 86400)
        msg = f'Resolver Query OK (pcid:{creature.id})'
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
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.instance is None:
        msg = f'Creature not in an instance (creature.id:{creature.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_effect  = RedisEffect(creature)
        creatures_effects = creatures_effect.get_all_instance()
    except Exception as e:
        msg = f'RedisEffect Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_status   = RedisStatus(creature)
        creatures_statuses = creatures_status.get_all_instance()
    except Exception as e:
        msg = f'RedisStatus Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creatures_cd  = RedisCd(creature)
        creatures_cds = creatures_cd.get_all_instance()
    except Exception as e:
        msg = f'RedisCd Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_pa = RedisPa(creature)
    except Exception as e:
        msg = f'RedisPa Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        instance = RedisInstance(creature=creature)
        map      = instance.map
    except Exception as e:
        msg = f'RedisInstance Query KO [{e}]'
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
        creatures          = fn_creatures_in_instance(creature.instance)
    except Exception as e:
        msg = f'ResolverInfo Query KO [{e}]'
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
            "instance": creature.instance,
            "creatures": creatures,
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

    msg = 'Context Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {"resolver": None,
                        "internal": payload},
        }
    ), 200
