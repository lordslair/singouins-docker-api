# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_instance_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: GET /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
@check_instance_exists
def get(creatureuuid, instanceuuid):
    if g.Instance.id:
        msg = f'{g.h} Instance({g.Instance.id}) Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Instance.as_dict(),
            }
        ), 200
    else:
        msg = f'{g.h} Instance({g.Instance.id}) Query KO - NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
