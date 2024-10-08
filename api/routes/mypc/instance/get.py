# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    )


# API: GET /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
def instance_get(creatureuuid, instanceuuid):

    msg = f'{g.h} Instance({g.Instance.id}) Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": g.Instance.to_mongo(),
        }
    ), 200
