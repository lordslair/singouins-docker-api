# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_korp      import *

from nosql                      import *

#
# Routes /mypc/{pcid}/korp
#
# API: POST /mypc/<int:pcid>/korp/<int:korpid>/accept
@jwt_required()
def korp_accept(pcid,korpid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200
    if pc.korp_rank != 'Pending':
        return jsonify({"success": False,
                        "msg": f'PC is not pending in a Korp (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200

    try:
        pc = fn_korp_set_rank(pc,korpid,'Member')
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** joined this Korp',
                    "embed": None,
                    "scope": f'Korp-{pc.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Korp accept OK (pcid:{pc.id},korpid:{korpid})',
                            "payload": korp}), 200

# API: POST /mypc/<int:pcid>/korp
@jwt_required()
def korp_create(pcid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    korpname = request.json.get('name',     None)
    if korpname is None:
        return jsonify({"success": False,
                        "msg": f'Korpname not found (korpname:{korpname})',
                        "payload": None}), 200

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409
    if pc.korp is not None:
        return jsonify({"success": False,
                        "msg": f'PC already in a Korp (pcid:{pc.id},korpid:{pc.korp})',
                        "payload": None}), 200

    # Remove everything, except alphanumeric, space, squote
    korpname = ''.join([c for c in korpname if c.isalnum() or c in [" ","'"]])
    # Size check
    if len(korpname) > 16:
        return jsonify({"success": False,
                        "msg": f'Korp name too long (korpname:{korpname})',
                        "payload": None}), 200
    # Unicity test
    if fn_korp_get_one_by_name(korpname):
        msg = f'Korp already exists (korpname:{korpname})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 409

    try:
        newkorp = fn_korp_add_one(pc,korpname)
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pcid},korpname:{korpname}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Korp created, let's assign the team creator in the korp
    try:
        pc = fn_korp_set_rank(pc,newkorp.id,'Leader')
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pcid},korpname:{korpname}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            korp = fn_korp_get_one(newkorp.id)
        except Exception as e:
            msg = f'Korp Query KO (korpid:{newkorp.id}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** created this Korp',
                    "embed": None,
                    "scope": f'Korp-{pc.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Korp create OK (pcid:{pc.id},korpid:{pc.korp})',
                            "payload": korp}), 201

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/decline
@jwt_required()
def korp_decline(pcid,korpid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200
    if pc.korp_rank == 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC cannot be the korp Leader (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200

    try:
        pc = fn_korp_set_rank(pc,None,None)
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qname = 'yarqueue:discord'
            qmsg  = {"ciphered": False,
                     "payload": f':information_source: **[{pc.id}] {pc.name}** declined this Korp',
                     "embed": None,
                     "scope": f'Korp-{korpid}'}
            logger.trace(f'{qname}:{qmsg}')
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qname = 'broadcast'
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            logger.trace(f'{qname}:{qmsg}')
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Korp decline OK (pcid:{pc.id},korpid:{korpid})',
                            "payload": korp}), 200

# API: DELETE /mypc/<int:pcid>/korp/<int:korpid>
@jwt_required()
def korp_delete(pcid,korpid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200
    if pc.korp_rank != 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC is not the korp Leader (pcid:{pc.id},korprank:{pc.korp_rank})',
                        "payload": None}), 200

    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    count = len(korp['members']) + len(korp['pending'])
    if count > 1:
        msg = f'Korp not empty (korpid:{korpid},members:{count})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        fn_korp_delete_one(korp['korp'].id)    # We delete the Korp
        fn_korp_set_rank(pc,None,None) # We empty Korp fields for the Leader
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": f':information_source: **[{pc.id}] {pc.name}** deleted this Korp',
                "embed": None,
                "scope": f'Korp-{korpid}'}
        queue.yqueue_put('yarqueue:discord', qmsg)
        # We put the info in queue for ws Front
        qmsg = {"ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/korp',
                "scope": 'korp'}
        queue.yqueue_put('broadcast', qmsg)

        return jsonify({"success": True,
                        "msg": f'Korp delete OK (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200

# API: GET /mypc/{pcid}/korp/{korpid}
@jwt_required()
def korp_get_one(pcid,korpid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200

    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if korp:
            return jsonify({"success": True,
                            "msg": f'Korp Query OK (pcid:{pc.id},korpid:{korpid})',
                            "payload": korp}), 200
        elif korp is False:
            return jsonify({"success": False,
                            "msg": f'Korp Query KO - Not Found (pcid:{pc.id},korpid:{korpid})',
                            "payload": None}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Korp Query KO - Failed (pcid:{pc.id},korpid:{korpid})',
                            "payload": None}), 200

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/invite/<int:targetid>
@jwt_required()
def korp_invite(pcid,korpid,targetid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200
    if pc.korp_rank != 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC is not the korp Leader (pcid:{pc.id},korprank:{pc.korp_rank})',
                        "payload": None}), 200
    if target is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (targetid:{targetid})',
                        "payload": None}), 200
    if target.korp is not None:
        return jsonify({"success": False,
                        "msg": f'PC invited is already in a Korp (pcid:{target.id},korpid:{target.korp})',
                        "payload": None}), 200

    # Korp population check
    try:
        korp = fn_korp_get_one(korpid)
    except Exception as e:
        msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    count      = len(korp['members']) + len(korp['pending'])
    maxmembers = 100
    if count == maxmembers:
        msg = f'Korp is already full (korpid:{korpid},members:{count}/{maxmembers})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        fn_korp_set_rank(target,korpid,'Pending') # We set Korp fields for the Target
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** invited **[{target.id}] {target.name}** in this Korp',
                    "embed": None,
                    "scope": f'Korp-{pc.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Korp invite OK (pcid:{pc.id},korpid:{korpid})',
                            "payload": korp}), 200

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/kick/<int:targetid>
@jwt_required()
def korp_kick(pcid,korpid,targetid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200
    if pc.korp_rank != 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC is not the korp Leader (pcid:{pc.id},korprank:{pc.korp_rank})',
                        "payload": None}), 200
    if target is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (targetid:{targetid})',
                        "payload": None}), 200
    if target.korp is None:
        return jsonify({"success": False,
                        "msg": f'PC kicked is not in a Korp (pcid:{target.id},korpid:{target.korp})',
                        "payload": None}), 200
    if pc.id == targetid:
        return (200,
                False,
                f'PC target cannot be the Korp Leader (pcid:{pcid},targetid:{targetid})',
                None)

    try:
        fn_korp_set_rank(target,None,None) # We empty Korp fields for the Target
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'Korp Query KO (pcid:{pc.id},korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws Discord
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** kicked **[{target.id}] {target.name}** from this Korp',
                    "embed": None,
                    "scope": f'Korp-{pc.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Korp kick OK (pcid:{pc.id},korpid:{korpid})',
                            "payload": korp}), 200

# API: /mypc/<int:pcid>/korp/<int:korpid>/leave
@jwt_required()
def korp_leave(pcid,korpid):
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
    if pc.korp != korpid:
        return jsonify({"success": False,
                        "msg": f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200
    if pc.korp_rank == 'Leader':
        return jsonify({"success": False,
                        "msg": f'PC cannot be the Korp Leader (pcid:{pc.id},korpid:{korpid})',
                        "payload": None}), 200

    try:
        fn_korp_set_rank(pc,None,None) # We empty Korp fields for the Member
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        try:
            korp = fn_korp_get_one(korpid)
        except Exception as e:
            msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** left this Korp',
                    "embed": None,
                    "scope": f'Korp-{korpid}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

            return jsonify({"success": True,
                            "msg": f'Korp leave OK (pcid:{pc.id},korpid:{korpid})',
                            "payload": None}), 200
