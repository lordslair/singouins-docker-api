# -*- coding: utf8 -*-

from flask import jsonify
from flask_jwt_extended import (get_jwt, jwt_required, JWTManager)
from loguru import logger

from utils.redis import r

from variables import API_ENV

# Initialize JWTManager for Flask
jwt = JWTManager()


# API: DELETE /auth/logout
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    try:
        r.set(f"{API_ENV}:auth:access_jti:{jti}", "revoked")  # Mark token as revoked in Redis
    except Exception as e:
        msg = f'JTI Revokation KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200
    else:
        msg = 'JTI Revokation OK'
        logger.trace(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200
