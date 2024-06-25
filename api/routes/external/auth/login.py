# -*- coding: utf8 -*-

import datetime

from flask import jsonify, request
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from loguru import logger

from mongo.models.User import UserDocument
from utils.decorators import check_is_json
from variables import TOKEN_DURATION


# API: POST /auth/login
@check_is_json
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify(
            {
                "msg": "Missing username parameter",
            }
        ), 400
    if not password:
        return jsonify(
            {
                "msg": "Missing password parameter",
            }
        ), 400

    try:
        if UserDocument.objects(name=username).count() > 0:
            # User exists
            User = UserDocument.objects(name=username).get()
            if not check_password_hash(User.hash, password):
                msg = "Wrong password"
                logger.warning(msg)
                return jsonify(
                    {
                        "msg": msg,
                    }
                ), 401
        else:
            msg = "Bad username"
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 401
    except Exception as e:
        msg = f'User Query KO (mail:{username}) [{e}]'
        logger.error(msg)

    # Identity can be any data that is json serializable
    msg = "Access Token Query OK"
    logger.trace(msg)
    return jsonify(
        {
            'access_token': create_access_token(
                identity=username,
                expires_delta=datetime.timedelta(minutes=TOKEN_DURATION)
            ),
            'refresh_token': create_refresh_token(identity=username)
        }
    ), 200
