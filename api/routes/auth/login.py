# -*- coding: utf8 -*-

import datetime

from flask import jsonify, request
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from loguru import logger
from pydantic import BaseModel, ValidationError

from mongo.models.User import UserDocument
from utils.decorators import check_is_json
from variables import TOKEN_DURATION


class LoginUserSchema(BaseModel):
    username: str
    password: str


# API: POST /auth/login
@check_is_json
def login():
    try:
        Login = LoginUserSchema(**request.json)  # Validate and parse the JSON data
    except ValidationError as e:
        return jsonify(
            {
                "success": False,
                "msg": "Validation and parsing error",
                "payload": e.errors(),
            }
        ), 400

    try:
        User = UserDocument.objects(name=Login.username).get()
    except UserDocument.DoesNotExist:
        logger.debug("UserDocument Query KO (404)")

    # If password mismatch
    if not check_password_hash(User.hash, Login.password):
        msg = "Wrong password"
        logger.warning(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 401

    # Identity can be any data that is json serializable
    logger.trace("Access Token Query OK")
    return jsonify(
        {
            'access_token': create_access_token(
                identity=Login.username,
                expires_delta=datetime.timedelta(minutes=TOKEN_DURATION)
            ),
            'refresh_token': create_refresh_token(identity=Login.username)
        }
    ), 200
