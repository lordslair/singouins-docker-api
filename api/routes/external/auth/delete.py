# -*- coding: utf8 -*-

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from loguru import logger
from pydantic import BaseModel, ValidationError

from mongo.models.User import UserDocument
from utils.decorators import check_is_json


class DeleteUserSchema(BaseModel):
    username: str


# API: DELETE /auth/delete
@jwt_required()
@check_is_json
def delete():
    try:
        Login = DeleteUserSchema(**request.json)  # Validate and parse the JSON data
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
        msg = 'UserDocument Query KO (404)'
        logger.warning(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200

    try:
        logger.debug(f'User deletion >> (username:{Login.username})')
        User.delete()
    except Exception as e:
        msg = f'User deletion KO (username:{Login.username}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200
    else:
        msg = f'User deletion OK (username:{Login.username})'
        logger.debug(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200
