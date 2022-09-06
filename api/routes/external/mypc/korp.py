# -*- coding: utf8 -*-

import json

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_korp      import (fn_korp_add_one,
                                        fn_korp_delete_one,
                                        fn_korp_get_one,
                                        fn_korp_get_one_by_name,
                                        fn_korp_set_rank)

from nosql.queue                import yqueue_put


#
# Routes /mypc/{pcid}/korp
#
# API: POST /mypc/<int:pcid>/korp/<int:korpid>/accept
@jwt_required()
def korp_accept(pcid, korpid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
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
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.korp_rank != 'Pending':
        msg = f'{h} Korp pending is required (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_korp_set_rank(creature, korpid, 'Member')
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": (f':information_source: '
                                f'**[{creature.id}] {creature.name}** '
                                f'joined this Korp'),
                    "embed": None,
                    "scope": f'Korp-{creature.korp}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Korp accept OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 200


# API: POST /mypc/<int:pcid>/korp
@jwt_required()
def korp_create(pcid):
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
    korpname = request.json.get('name', None)
    if korpname is None:
        msg = f'Korpname not found (korpname:{korpname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Remove everything, except alphanumeric, space, squote
    korpname = ''.join([c for c in korpname if c.isalnum() or c in [" ", "'"]])
    # Size check
    if len(korpname) > 16:
        msg = f'Korp name too long (korpname:{korpname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Unicity test
    if fn_korp_get_one_by_name(korpname):
        msg = f'Korp already exists (korpname:{korpname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    # Pre-flight checks
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
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp is not None:
        msg = f'{h} PC already in a Korp (korpid:{creature.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        newkorp = fn_korp_add_one(creature, korpname)
    except Exception as e:
        msg = f'{h} Korp Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Korp created, let's assign the team creator in the korp
    try:
        fn_korp_set_rank(creature, newkorp.id, 'Leader')
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{newkorp.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            korp = fn_korp_get_one(newkorp.id)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{newkorp.id}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": (f':information_source: '
                                f'**[{creature.id}] {creature.name}** '
                                f'created this Korp'),
                    "embed": None,
                    "scope": f'Korp-{creature.korp}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Korp create OK (korpid:{creature.korp})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 201


# API: POST /mypc/<int:pcid>/korp/<int:korpid>/decline
@jwt_required()
def korp_decline(pcid, korpid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
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
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.korp_rank == 'Leader':
        msg = f'{h} PC cannot be the korp Leader (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_korp_set_rank(creature, None, None)
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for ws
            qname = 'yarqueue:discord'
            qmsg  = {"ciphered": False,
                     "payload": (f':information_source: '
                                 f'**[{creature.id}] {creature.name}** '
                                 f'declined this Korp'),
                     "embed": None,
                     "scope": f'Korp-{korpid}'}
            logger.trace(f'{qname}:{qmsg}')
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qname = 'broadcast'
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            logger.trace(f'{qname}:{qmsg}')
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Korp decline OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 200


# API: DELETE /mypc/<int:pcid>/korp/<int:korpid>
@jwt_required()
def korp_delete(pcid, korpid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
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
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.korp_rank != 'Leader':
        msg = f'{h} PC is not the korp Leader (korpid:{creature.korp_rank})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count = len(korp['members']) + len(korp['pending'])
    if count > 1:
        msg = f'Korp not empty (korpid:{korpid},members:{count})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_korp_delete_one(korp['korp'].id)   # We delete the Korp
        fn_korp_set_rank(creature, None, None)  # We empty Leader Korp fields
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": (f':information_source: '
                            f'**[{creature.id}] {creature.name}** '
                            f'deleted this Korp'),
                "embed": None,
                "scope": f'Korp-{korpid}'}
        yqueue_put('yarqueue:discord', qmsg)
        # We put the info in queue for ws Front
        qmsg = {"ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/korp',
                "scope": 'korp'}
        yqueue_put('broadcast', qmsg)

        msg = f'{h} Korp delete OK (korpid:{korpid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200


# API: GET /mypc/{pcid}/korp/{korpid}
@jwt_required()
def korp_get_one(pcid, korpid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
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
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if korp:
            msg = f'{h} Korp Query OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 200
        elif korp is False:
            msg = f'{h} Korp Query KO - Not Found (korpid:{korpid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'{h} Korp Query KO - Failed (korpid:{korpid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /mypc/<int:pcid>/korp/<int:korpid>/invite/<int:targetid>
@jwt_required()
def korp_invite(pcid, korpid, targetid):
    target   = fn_creature_get(None, targetid)[3]
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None or target is None:
        msg = f'Creature not found (creatureid:{pcid},target:({targetid}))'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.korp_rank != 'Leader':
        msg = f'{h} PC should be the korp Leader (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if target.korp is not None:
        msg = f'{h} Already in Korp (pcid:{target.id},korpid:{target.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Korp population check
    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count      = len(korp['members']) + len(korp['pending'])
    maxmembers = 100
    if count == maxmembers:
        members = f'{count}/{maxmembers}'
        msg = f'{h} Korp Full (korpid:{korpid},members:{members})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_korp_set_rank(target, korpid, 'Pending')  # We set Target Korp
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": (f':information_source: '
                                f'**[{creature.id}] {creature.name}** '
                                f'invited '
                                f'**[{target.id}] {target.name}** '
                                f'in this Korp'),
                    "embed": None,
                    "scope": f'Korp-{creature.korp}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Korp invite OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 200


# API: POST /mypc/<int:pcid>/korp/<int:korpid>/kick/<int:targetid>
@jwt_required()
def korp_kick(pcid, korpid, targetid):
    target   = fn_creature_get(None, targetid)[3]
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None or target is None:
        msg = f'Creature not found (creatureid:{pcid},target:({targetid}))'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.korp_rank != 'Leader':
        msg = f'{h} PC should be the korp Leader (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if target.korp is None:
        msg = f'{h} Should be in Korp (korpid:{target.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if target.id == creature.id:
        msg = f'{h} Cannot kick yourself (korpid:{target.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_korp_set_rank(target, None, None)  # We empty Target Korp fields
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for ws Discord
            qmsg = {"ciphered": False,
                    "payload": (f':information_source: '
                                f'**[{creature.id}] {creature.name}** '
                                f'kicked '
                                f'**[{target.id}] {target.name}** '
                                f'from this Korp'),
                    "embed": None,
                    "scope": f'Korp-{creature.korp}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Korp kick OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 200


# API: /mypc/<int:pcid>/korp/<int:korpid>/leave
@jwt_required()
def korp_leave(pcid, korpid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
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
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.korp_rank == 'Leader':
        msg = f'{h} PC cannot be the korp Leader (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_korp_set_rank(creature, None, None)  # We empty Member Korp fields
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": (f':information_source: '
                                f'**[{creature.id}] {creature.name}** '
                                f'left this Korp'),
                    "embed": None,
                    "scope": f'Korp-{korpid}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Korp leave OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": korp,
                }
            ), 200
