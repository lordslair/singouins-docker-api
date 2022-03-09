# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_mp        import *

#
# Routes /mypc/{pcid}/mp
#
# API: POST /mypc/{pcid}/mp
@jwt_required()
def mp_add(pcid):
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    pcsrcid = request.json.get('src',     None)
    dsts    = request.json.get('dst',     None)
    subject = request.json.get('subject', None)
    body    = request.json.get('body',    None)
    pcsrc   = fn_creature_get(None,pcsrcid)[3]

    if pcsrc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcsrc})',
                        "payload": None}), 200
    if pcsrc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pcsrc.id},username:{user.name})',
                        "payload": None}), 409

    try:
        success = fn_mp_add(pcsrc,pcsrcid,dsts,subject,body)
    except Exception as e:
        msg = f'MP creation KO (srcid:{pcsrc.id},dstid:{dsts}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if success:
            return jsonify({"success": True,
                            "msg": f'MP creation OK (pcid:{pcsrc.id})',
                            "payload": None}), 201
        else:
            return jsonify({"success": True,
                            "msg": f'MP creation KO (pcid:{pcsrc.id})',
                            "payload": None}), 200

# API: DELETE /mypc/{pcid}/mp/{mpid}
@jwt_required()
def mp_del(pcid,mpid):
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

    try:
        success = fn_mp_del_one(pc,mpid)
    except Exception as e:
        msg = f'MP deletion KO (pcid:{pc.id},mpid:{mpid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if success:
            return jsonify({"success": True,
                            "msg": f'MP deletion OK (pcid:{pc.id})',
                            "payload": None}), 200
        else:
            return jsonify({"success": True,
                            "msg": f'MP deletion KO (pcid:{pc.id})',
                            "payload": None}), 200

# API: GET /mypc/{pcid}/mp/{mpid}
@jwt_required()
def mp_get_one(pcid,mpid):
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

    try:
        mp = fn_mp_get_one(pc,mpid)
    except Exception as e:
        msg = f'MP query failed (pcid:{pc.id},mpid:{mpid})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if mp:
            return jsonify({"success": True,
                            "msg": f'MP Query OK (pcid:{pc.id})',
                            "payload": mp}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'MP Query KO (pcid:{pc.id})',
                            "payload": None}), 200

# API: GET /mypc/{pcid}/mp
@jwt_required()
def mp_get_all(pcid):
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

    try:
        mps = fn_mp_get_all(pc)
    except Exception as e:
        msg = f'MPs query failed (pcid:{pc.id},mpid:{mpid})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if mps:
            return jsonify({"success": True,
                            "msg": f'MPs Query OK (pcid:{pc.id})',
                            "payload": mps}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'MPs Query KO (pcid:{pc.id})',
                            "payload": None}), 200

# API: GET /mypc/{pcid}/mp/addressbook
@jwt_required()
def addressbook_get(pcid):
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

    try:
        addressbook = fn_mp_addressbook_get(pc)
    except Exception as e:
        msg = f'Addressbook query failed (pcid:{pc.id})'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if addressbook:
            return jsonify({"success": True,
                            "msg": f'Addressbook Query OK (pcid:{pc.id})',
                            "payload": [{"id": row[0], "name": row[1]} for row in addressbook]}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Addressbook Query KO (pcid:{pc.id})',
                            "payload": None}), 200
