# -*- coding: utf8 -*-

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger

from mongo.models.User import UserDocument
from utils.decorators import check_is_json


# API: DELETE /auth/delete
@jwt_required()
@check_is_json
def delete():
    username = request.json.get('username', None)
    current_user = get_jwt_identity()

    if not username:
        return jsonify(
            {
                "msg": "Missing username parameter",
            }
        ), 400
    if username != current_user:
        return jsonify(
            {
                "msg": "Token/username mismatch",
            }
        ), 400

    try:
        User = UserDocument.objects(name=username).first()

        if User:
            logger.debug(f'User deletion >> (username:{username})')
            User.delete()
            msg = f'User deletion OK (username:{username})'
            logger.debug(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 200
        else:
            msg = f'User deletion KO (username:{username}) NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 200
    except Exception as e:
        msg = f'User deletion KO (username:{username}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200
