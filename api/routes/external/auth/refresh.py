# -*- coding: utf8 -*-

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from loguru import logger


# API: POST /auth/refresh
@jwt_required(refresh=True)
def refresh():
    msg = "Refresh Token Query OK"
    logger.trace(msg)
    return jsonify(
        {
            'access_token': create_access_token(identity=get_jwt_identity())
        }
    ), 200
