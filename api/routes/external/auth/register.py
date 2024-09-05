# -*- coding: utf8 -*-

import uuid

from flask import jsonify, request
from flask_bcrypt import generate_password_hash
from loguru import logger
from pydantic import BaseModel, ValidationError

from utils.mail import send
from utils.token import generate_confirmation_token
from mongo.models.User import UserDocument, UserDiscord
from utils.decorators import check_is_json
from variables import (
    API_URL,
    DATA_PATH,
    DISCORD_URL,
    )


class RegisterUserSchema(BaseModel):
    mail: str
    password: str


# API: POST /auth/register
@check_is_json
def register():
    try:
        Register = RegisterUserSchema(**request.json)  # Validate and parse the JSON data
    except ValidationError as e:
        return jsonify(
            {
                "success": False,
                "msg": "Validation and parsing error",
                "payload": e.errors(),
            }
        ), 400

    # Check User existence
    try:
        User = UserDocument.objects(name=Register.mail).get()
    except UserDocument.DoesNotExist:
        # We can create the User
        pass
    else:
        # We return an error (duplicate user)
        msg = f"User already exists (mail:{Register.mail})"
        logger.debug(msg)
        return jsonify(
            {
                "msg": msg,
                "user": User.to_mongo().to_dict(),
            }
        ), 409

    try:
        newUser = UserDocument(
            _id=uuid.uuid3(uuid.NAMESPACE_DNS, Register.mail),
            discord=UserDiscord(),
            hash=generate_password_hash(Register.password, rounds=10),
            name=Register.mail,
        )
        newUser.save()
    except Exception as e:
        msg = f'User Creation KO (mail:{Register.mail}) [{e}]'
        logger.error(msg)

    # User created, we send email
    subject = '[🐒&🐖] Bienvenue chez le Singouins !'
    token = generate_confirmation_token(Register.mail)
    url = f'{API_URL}/auth/confirm/{token}'
    body = open(f"{DATA_PATH}/registered.html", "r").read()

    if send(
        Register.mail,
        subject,
        body.format(
            urllogo='[INSERT LOGO HERE]',
            urlconfirm=url,
            urldiscord=DISCORD_URL
            )
    ):
        msg = "User successfully added | mail OK"
        logger.debug(msg)
        return jsonify(
            {
                "msg": msg,
                "user": newUser.to_mongo().to_dict(),
            }
        ), 201
    else:
        msg = "User successfully added | mail KO"
        logger.warning(msg)
        return jsonify(
            {
                "msg": msg,
                "user": newUser.to_mongo().to_dict(),
            }
        ), 200
