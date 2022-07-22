# -*- coding: utf8 -*-

import requests

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_creatures import fn_creatures_in_instance
from mysql.methods.fn_user      import fn_user_get

from nosql                      import * # Custom internal module for Redis queries
from nosql.models.RedisPa       import *
from nosql.models.RedisEvent    import *
from nosql.models.RedisCd       import *
from nosql.models.RedisEffect   import *
from nosql.models.RedisStatus   import *

from variables                  import RESOLVER_URL

#
# Routes /mypc/{pcid}/action/resolver/*
#
# API: POST /mypc/{pcid}/action/resolver/skill/{skill_name}
@jwt_required()
def action_resolver_skill(pcid,skill_name):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        msg = f'Missing JSON in request'
        logger.warn(msg)
        return jsonify({"msg": msg,
                        "success": False,
                        "payload": None}), 400
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.instance is None:
        return jsonify({"success": False,
                        "msg": f'Creature not in an instance (pcid:{pcid})',
                        "payload": None}), 200

    try:
        redis_cd    = RedisStatus(pc)
        creature_cd = redis_cd.get(skill_name)
    except Exception as e:
        msg = f'CDs Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_cd:
            # The skill was already used, and still on CD
            msg = f'Skill already on CD (pcid:{pc.id},skill_name:{skill_name})'
            logger.debug(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": cd}), 200

    try:
        fightEventname     = request.json.get('name',     None)
        fightEventtype     = request.json.get('type',     None)
        fightEventactor    = request.json.get('actor',    None)
        fightEventparams   = request.json.get('params',   None)
        map                = instances.get_instance(pc.instance)['map']
        creatures          = fn_creatures_in_instance(pc.instance)
        creatures_effect   = RedisEffect(pc)
        creatures_effects  = creatures_effect.get_all_instance()
        creatures_status   = RedisStatus(pc)
        creatures_statuses = creatures_status.get_all_instance()
        creatures_cd       = RedisCd(pc)
        creatures_cds      = creatures_cd.get_all_instance()
        pas                = RedisPa(pc).get()
    except Exception as e:
        msg = f'ResolverInfo Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Everythins if fine, we can build the payload
    # Supposedly got all infos
    payload = { "context": {
                    "map": map,
                    "instance": pc.instance,
                    "creatures": creatures,
                    "effects": creatures_effects,
                    "status": creatures_statuses,
                    "cd": creatures_cds,
                    "pa": pas
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
        response  = requests.post(f'{RESOLVER_URL}/', json = payload)
    except Exception as e:
        msg = f'Resolver Query KO (pcid:{pc.id},skill_name:{skill_name}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We create the Creature Event
        RedisEvent(pc).add(pc.id,
                           None,
                           'skill',
                           f'Used a Skill ({skill_name})',
                           30*86400)
        msg = f'Resolver Query OK (pcid:{pc.id})'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": {"resolver": json.loads(response.text),
                                    "internal": payload}}), 200

# API: POST /mypc/{pcid}/action/resolver/move
@jwt_required()
def action_resolver_move(pcid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        msg = f'Missing JSON in request'
        logger.warn(msg)
        return jsonify({"msg": msg, "success": False, "payload": None}), 400
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.instance is None:
        return jsonify({"success": False,
                        "msg": f'Creature not in an instance (pcid:{pcid})',
                        "payload": None}), 200

    try:
        fightEventname     = request.json.get('name',     None)
        fightEventtype     = request.json.get('type',     None)
        fightEventactor    = request.json.get('actor',    None)
        fightEventparams   = request.json.get('params',   None)
        map                = instances.get_instance(pc.instance)['map']
        creatures          = fn_creatures_in_instance(pc.instance)
        creatures_effect   = RedisEffect(pc)
        creatures_effects  = creatures_effect.get_all_instance()
        creatures_status   = RedisStatus(pc)
        creatures_statuses = creatures_status.get_all_instance()
        creatures_cd       = RedisCd(pc)
        creatures_cds      = creatures_cd.get_all_instance()
        pas                = RedisPa(pc).get()
    except Exception as e:
        msg = f'ResolverInfo Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Supposedly got all infos
    payload = { "context": {
                    "map": map,
                    "instance": pc.instance,
                    "creatures": creatures,
                    "effects": creatures_effects,
                    "status": creatures_statuses,
                    "cd": creatures_cds,
                    "pa": pas
                  },
                  "fightEvent": {
                     "name": fightEventname,
                     "type": fightEventtype,
                     "actor": fightEventactor,
                     "params": fightEventparams
                  }
              }

    try:
        response  = requests.post(f'{RESOLVER_URL}/', json = payload)
    except Exception as e:
        msg = f'Resolver Query KO - Failed (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We create the Creature Event
        RedisEvent(pc).add(pc.id,
                           None,
                           'action',
                           'Moved',
                           30*86400)
        msg = f'Resolver Query OK (pcid:{pc.id})'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": {"resolver": json.loads(response.text),
                                    "internal": payload}}), 200

# API: POST /mypc/{pcid}/action/resolver/context
@jwt_required()
def action_resolver_context(pcid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        msg = f'Missing JSON in request'
        logger.warn(msg)
        return jsonify({"msg": msg, "success": False, "payload": None}), 400
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.instance is None:
        return jsonify({"success": False,
                        "msg": f'Creature not in an instance (pcid:{pcid})',
                        "payload": None}), 200

    try:
        fightEventname     = request.json.get('name',     None)
        fightEventtype     = request.json.get('type',     None)
        fightEventactor    = request.json.get('actor',    None)
        fightEventparams   = request.json.get('params',   None)
        map                = instances.get_instance(pc.instance)['map']
        creatures          = fn_creatures_in_instance(pc.instance)
        creatures_effect   = RedisEffect(pc)
        creatures_effects  = creatures_effect.get_all_instance()
        creatures_status   = RedisStatus(pc)
        creatures_statuses = creatures_status.get_all_instance()
        creatures_cd       = RedisCd(pc)
        creatures_cds      = creatures_cd.get_all_instance()
        pas                = RedisPa(pc).get()
    except Exception as e:
        msg = f'ResolverInfo Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Supposedly got all infos
    payload = { "context": {
                    "map": map,
                    "instance": pc.instance,
                    "creatures": creatures,
                    "effects": creatures_effects,
                    "status": creatures_statuses,
                    "cd": creatures_cds,
                    "pa": pas
                  },
                  "fightEvent": {
                     "name": fightEventname,
                     "type": fightEventtype,
                     "actor": fightEventactor,
                     "params": fightEventparams
                  }
              }

    return jsonify({"success": True,
                    "msg": "Context Query OK",
                    "payload": {"resolver": None,
                                "internal": payload}}), 200
