# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.models.RedisCd       import *

#
# Routes /mypc/{pcid}/cds
#
# API: GET /mypc/{pcid}/cds
@jwt_required()
def cds_get(pcid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409

    try:
        pc_cd  = RedisCd(pc)
        pc_cds = pc_cd.get_all()
    except Exception as e:
        msg = f'CDs Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'CDs Query OK (pcid:{pc.id})',
                        "payload": {"cds":      pc_cds,
                                    "creature": pc}}), 200
