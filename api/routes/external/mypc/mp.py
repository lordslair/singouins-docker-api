# -*- coding: utf8 -*-

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_mp        import (fn_mp_add,
                                        fn_mp_del_one,
                                        fn_mp_get_one,
                                        fn_mp_get_all,
                                        fn_mp_addressbook_get)


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
    pcsrcid = request.json.get('src', None)
    dsts    = request.json.get('dst', None)
    subject = request.json.get('subject', None)
    body    = request.json.get('body', None)
    pcsrc   = fn_creature_get(None, pcsrcid)[3]

    # Pre-flight checks
    if pcsrc is None:
        msg = f'Creature not found (creatureid:{pcsrc})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if pcsrc.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{pcsrc.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        success = fn_mp_add(pcsrc, pcsrcid, dsts, subject, body)
    except Exception as e:
        msg = f'MP creation KO (srcid:{pcsrc.id},dstid:{dsts}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if success:
            msg = f'MP creation OK (pcid:{pcsrc.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": None,
                }
            ), 201
        else:
            msg = f'MP creation KO (pcid:{pcsrc.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: DELETE /mypc/{pcid}/mp/{mpid}
@jwt_required()
def mp_del(pcid, mpid):
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

    try:
        success = fn_mp_del_one(creature, mpid)
    except Exception as e:
        msg = f'MP deletion KO (pcid:{creature.id},mpid:{mpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if success:
            msg = f'MP deletion OK (pcid:{creature.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'MP deletion KO (pcid:{creature.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /mypc/{pcid}/mp/{mpid}
@jwt_required()
def mp_get_one(pcid, mpid):
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

    try:
        mp = fn_mp_get_one(creature, mpid)
    except Exception as e:
        msg = f'MP Query KO (pcid:{creature.id},mpid:{mpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if mp:
            msg = f'MP Query OK (pcid:{creature.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": mp,
                }
            ), 200
        else:
            msg = f'MP Query KO (pcid:{creature.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /mypc/{pcid}/mp
@jwt_required()
def mp_get_all(pcid):
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

    try:
        mps = fn_mp_get_all(creature)
    except Exception as e:
        msg = f'MPs Query KO (pcid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if mps:
            msg = f'MPs Query OK (pcid:{creature.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": mps,
                }
            ), 200
        else:
            msg = f'MPs Query KO (pcid:{creature.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /mypc/{pcid}/mp/addressbook
@jwt_required()
def addressbook_get(pcid):
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

    try:
        addressbook = fn_mp_addressbook_get(creature)
    except Exception as e:
        msg = f'Addressbook Query KO (pcid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if addressbook:
            payload = [{"id": row[0], "name": row[1]} for row in addressbook]
            msg = f'Addressbook Query OK (pcid:{creature.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": payload,
                }
            ), 200
        else:
            msg = f'Addressbook Query KO (pcid:{creature.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
