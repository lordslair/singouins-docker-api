# -*- coding: utf8 -*-

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger


# API: GET /auth/infos
@jwt_required()
def infos():
    msg = "User Query OK"
    logger.trace(msg)
    # Access the identity of the current user with get_jwt_identity
    return jsonify(
        logged_in_as=get_jwt_identity(),
        ), 200
