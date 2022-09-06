# -*- coding: utf8 -*-

import json

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_squad     import (fn_squad_add_one,
                                        fn_squad_delete_one,
                                        fn_squad_get_one,
                                        fn_squad_set_rank)

from nosql.queue                import yqueue_put


#
# Routes /mypc/{pcid}/squad
#
# API: POST /mypc/<int:pcid>/squad/<int:squadid>/accept
@jwt_required()
def squad_accept(pcid, squadid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.squad_rank != 'Pending':
        msg = f'{h} Squad pending is required (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_squad_set_rank(creature, squadid, 'Member')
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
                                f'joined this Squad'),
                    "embed": None,
                    "scope": f'Squad-{creature.squad}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Squad accept OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200


# API: POST /mypc/<int:pcid>/squad
@jwt_required()
def squad_create(pcid):
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
    if creature.squad is not None:
        msg = f'{h} PC already in a Squad (squadid:{creature.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        newsquad = fn_squad_add_one(creature)
    except Exception as e:
        msg = f'{h} Squad Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Squad created, let's assign the team creator in the squad
    try:
        fn_squad_set_rank(creature, newsquad.id, 'Leader')
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{newsquad.id}) [{e}]'
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
            squad = fn_squad_get_one(newsquad.id)
        except Exception as e:
            msg = f'{h} Squad Query KO (squadid:{newsquad.id}) [{e}]'
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
                                f'created this Squad'),
                    "embed": None,
                    "scope": f'Squad-{creature.squad}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Squad create OK (squadid:{creature.squad})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 201


# API: POST /mypc/<int:pcid>/squad/<int:squadid>/decline
@jwt_required()
def squad_decline(pcid, squadid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.squad_rank == 'Leader':
        msg = f'{h} PC cannot be the squad Leader (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_squad_set_rank(creature, None, None)
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
                                 f'declined this Squad'),
                     "embed": None,
                     "scope": f'Squad-{squadid}'}
            logger.trace(f'{qname}:{qmsg}')
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qname = 'broadcast'
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            logger.trace(f'{qname}:{qmsg}')
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Squad decline OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200


# API: DELETE /mypc/<int:pcid>/squad/<int:squadid>
@jwt_required()
def squad_delete(pcid, squadid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.squad_rank != 'Leader':
        msg = f'{h} PC is not the squad Leader (squadid:{creature.squad_rank})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count = len(squad['members']) + len(squad['pending'])
    if count > 1:
        msg = f'Squad not empty (squadid:{squadid},members:{count})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_squad_delete_one(squad['squad'].id)   # We delete the Squad
        fn_squad_set_rank(creature, None, None)  # We empty Leader Squad fields
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
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
                            f'deleted this Squad'),
                "embed": None,
                "scope": f'Squad-{squadid}'}
        yqueue_put('yarqueue:discord', qmsg)
        # We put the info in queue for ws Front
        qmsg = {"ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/squad',
                "scope": 'squad'}
        yqueue_put('broadcast', qmsg)

        msg = f'{h} Squad delete OK (squadid:{squadid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200


# API: GET /mypc/{pcid}/squad/{squadid}
@jwt_required()
def squad_get_one(pcid, squadid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if squad:
            msg = f'{h} Squad Query OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200
        elif squad is False:
            msg = f'{h} Squad Query KO - Not Found (squadid:{squadid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'{h} Squad Query KO - Failed (squadid:{squadid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /mypc/<int:pcid>/squad/<int:squadid>/invite/<int:targetid>
@jwt_required()
def squad_invite(pcid, squadid, targetid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.squad_rank != 'Leader':
        msg = f'{h} PC should be the squad Leader (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if target.squad is not None:
        msg = f'{h} Already in Squad (pcid:{target.id},squadid:{target.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Squad population check
    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count      = len(squad['members']) + len(squad['pending'])
    maxmembers = 100
    if count == maxmembers:
        members = f'{count}/{maxmembers}'
        msg = f'{h} Squad Full (squadid:{squadid},members:{members})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_squad_set_rank(target, squadid, 'Pending')  # We set Target Squad
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
                                f'in this Squad'),
                    "embed": None,
                    "scope": f'Squad-{creature.squad}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Squad invite OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200


# API: POST /mypc/<int:pcid>/squad/<int:squadid>/kick/<int:targetid>
@jwt_required()
def squad_kick(pcid, squadid, targetid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.squad_rank != 'Leader':
        msg = f'{h} PC should be the squad Leader (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if target.squad is None:
        msg = f'{h} Should be in Squad (squadid:{target.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if target.id == creature.id:
        msg = f'{h} Cannot kick yourself (squadid:{target.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_squad_set_rank(target, None, None)  # We empty Target Squad fields
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
                                f'from this Squad'),
                    "embed": None,
                    "scope": f'Squad-{creature.squad}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Squad kick OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200


# API: /mypc/<int:pcid>/squad/<int:squadid>/leave
@jwt_required()
def squad_leave(pcid, squadid):
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
    if creature.squad != squadid:
        msg = f'{h} Squad request outside of your scope (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if creature.squad_rank == 'Leader':
        msg = f'{h} PC cannot be the squad Leader (squadid:{squadid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        fn_squad_set_rank(creature, None, None)  # We empty Member Squad fields
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squadid:{squadid}) [{e}]'
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
                                f'left this Squad'),
                    "embed": None,
                    "scope": f'Squad-{squadid}'}
            yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            msg = f'{h} Squad leave OK (squadid:{squadid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": squad,
                }
            ), 200
