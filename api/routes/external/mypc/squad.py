# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_squad     import *

from nosql                      import *

#
# Routes /mypc/{pcid}/squad
#
# API: POST /mypc/<int:pcid>/squad/<int:squadid>/accept
@jwt_required()
def squad_accept(pcid,squadid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200
    if pc.squad_rank != 'Pending':
        return jsonify({"success": False,
                        "msg": f'PC is not pending in a Squad (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200

    try:
        pc = fn_squad_set_rank(pc,squadid,'Member')
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** joined this Squad',
                    "embed": None,
                    "scope": f'Squad-{pc.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Squad accept OK (pcid:{pc.id},squadid:{squadid})',
                            "payload": squad}), 200

# API: POST /mypc/<int:pcid>/squad
@jwt_required()
def squad_create(pcid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad is not None:
        return jsonify({"success": False,
                        "msg": f'PC already in a Squad (pcid:{pc.id},squadid:{pc.squad})',
                        "payload": None}), 200

    try:
        newsquad = fn_squad_add_one(pc)
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pcid},squadname:{squadname}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Squad created, let's assign the team creator in the squad
    try:
        pc = fn_squad_set_rank(pc,newsquad.id,'Leader')
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pcid},squadname:{squadname}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            squad = fn_squad_get_one(newsquad.id)
        except Exception as e:
            msg = f'Squad Query KO (squadid:{newsquad.id}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** created this Squad',
                    "embed": None,
                    "scope": f'Squad-{pc.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Squad create OK (pcid:{pc.id},squadid:{pc.squad})',
                            "payload": squad}), 201

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/decline
@jwt_required()
def squad_decline(pcid,squadid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200
    if pc.squad_rank == 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC cannot be the squad Leader (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200

    try:
        pc = fn_squad_set_rank(pc,None,None)
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qname = 'yarqueue:discord'
            qmsg  = {"ciphered": False,
                     "payload": f':information_source: **[{pc.id}] {pc.name}** declined this Squad',
                     "embed": None,
                     "scope": f'Squad-{squadid}'}
            logger.trace(f'{qname}:{qmsg}')
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qname = 'broadcast'
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            logger.trace(f'{qname}:{qmsg}')
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Squad decline OK (pcid:{pc.id},squadid:{squadid})',
                            "payload": squad}), 200

# API: DELETE /mypc/<int:pcid>/squad/<int:squadid>
@jwt_required()
def squad_delete(pcid,squadid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200
    if pc.squad_rank != 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC is not the squad Leader (pcid:{pc.id},squadrank:{pc.squad_rank})',
                        "payload": None}), 200

    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    count = len(squad['members']) + len(squad['pending'])
    if count > 1:
        msg = f'Squad not empty (squadid:{squadid},members:{count})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        fn_squad_delete_one(squad['squad'].id)    # We delete the Squad
        fn_squad_set_rank(pc,None,None) # We empty Squad fields for the Leader
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": f':information_source: **[{pc.id}] {pc.name}** deleted this Squad',
                "embed": None,
                "scope": f'Squad-{squadid}'}
        queue.yqueue_put('yarqueue:discord', qmsg)
        # We put the info in queue for ws Front
        qmsg = {"ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/squad',
                "scope": 'squad'}
        queue.yqueue_put('broadcast', qmsg)

        return jsonify({"success": True,
                        "msg": f'Squad delete OK (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200

# API: GET /mypc/{pcid}/squad/{squadid}
@jwt_required()
def squad_get_one(pcid,squadid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200

    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if squad:
            return jsonify({"success": True,
                            "msg": f'Squad Query OK (pcid:{pc.id},squadid:{squadid})',
                            "payload": squad}), 200
        elif squad is False:
            return jsonify({"success": False,
                            "msg": f'Squad Query KO - Not Found (pcid:{pc.id},squadid:{squadid})',
                            "payload": None}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Squad Query KO - Failed (pcid:{pc.id},squadid:{squadid})',
                            "payload": None}), 200

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/invite/<int:targetid>
@jwt_required()
def squad_invite(pcid,squadid,targetid):
    target   = fn_creature_get(None,targetid)[3]
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200
    if pc.squad_rank != 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC is not the squad Leader (pcid:{pc.id},squadrank:{pc.squad_rank})',
                        "payload": None}), 200
    if target is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (targetid:{targetid})',
                        "payload": None}), 200
    if target.squad is not None:
        return jsonify({"success": False,
                        "msg": f'PC invited is already in a Squad (pcid:{target.id},squadid:{target.squad})',
                        "payload": None}), 200

    # Squad population check
    try:
        squad = fn_squad_get_one(squadid)
    except Exception as e:
        msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    count      = len(squad['members']) + len(squad['pending'])
    maxmembers = 100
    if count == maxmembers:
        msg = f'Squad is already full (squadid:{squadid},members:{count}/{maxmembers})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        fn_squad_set_rank(target,squadid,'Pending') # We set Squad fields for the Target
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** invited **[{target.id}] {target.name}** in this Squad',
                    "embed": None,
                    "scope": f'Squad-{pc.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Squad invite OK (pcid:{pc.id},squadid:{squadid})',
                            "payload": squad}), 200

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/kick/<int:targetid>
@jwt_required()
def squad_kick(pcid,squadid,targetid):
    target   = fn_creature_get(None,targetid)[3]
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200
    if pc.squad_rank != 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC is not the squad Leader (pcid:{pc.id},squadrank:{pc.squad_rank})',
                        "payload": None}), 200
    if target is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (targetid:{targetid})',
                        "payload": None}), 200
    if target.squad is None:
        return jsonify({"success": False,
                        "msg": f'PC kicked is not in a Squad (pcid:{target.id},squadid:{target.squad})',
                        "payload": None}), 200
    if pc.id == targetid:
        return (200,
                False,
                f'PC target cannot be the Squad Leader (pcid:{pcid},targetid:{targetid})',
                None)

    try:
        fn_squad_set_rank(target,None,None) # We empty Squad fields for the Target
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'Squad Query KO (pcid:{pc.id},squadid:{squadid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws Discord
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** kicked **[{target.id}] {target.name}** from this Squad',
                    "embed": None,
                    "scope": f'Squad-{pc.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Squad kick OK (pcid:{pc.id},squadid:{squadid})',
                            "payload": squad}), 200

# API: /mypc/<int:pcid>/squad/<int:squadid>/leave
@jwt_required()
def squad_leave(pcid,squadid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.squad != squadid:
        return jsonify({"success": False,
                        "msg": f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200
    if pc.squad_rank == 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC cannot be the Squad Leader (pcid:{pc.id},squadid:{squadid})',
                        "payload": None}), 200

    try:
        fn_squad_set_rank(pc,None,None) # We empty Squad fields for the Member
    except Exception as e:
        msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            squad = fn_squad_get_one(squadid)
        except Exception as e:
            msg = f'Squad Query KO (squadid:{squadid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** left this Squad',
                    "embed": None,
                    "scope": f'Squad-{squadid}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Squad leave OK (pcid:{pc.id},squadid:{squadid})',
                            "payload": None}), 200
