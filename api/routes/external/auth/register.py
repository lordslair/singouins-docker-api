# -*- coding: utf8 -*-

import uuid

from flask import jsonify, request
from flask_bcrypt import generate_password_hash
from loguru import logger

from utils.mail import send
from utils.token import generate_confirmation_token
from mongo.models.User import UserDocument, UserDiscord
from utils.decorators import check_is_json
from variables import (
    API_URL,
    DATA_PATH,
    DISCORD_URL,
    )


# API: POST /auth/register
@check_is_json
def register():
    password = request.json.get('password', None)
    mail = request.json.get('mail', None)
    if not mail:
        return jsonify(
            {
                "msg": "Missing mail parameter",
            }
        ), 400
    if not password:
        return jsonify(
            {
                "msg": "Missing password parameter",
            }
        ), 400

    # Check User existence
    try:
        if UserDocument.objects(name=mail).count() > 0:
            msg = f"User already exists (mail:{mail})"
            logger.debug(msg)
            return jsonify(
                {
                    "msg": msg,
                    "user": UserDocument.objects(name=mail).first().to_mongo().to_dict(),
                }
            ), 409
        else:
            newUser = UserDocument(
                _id=uuid.uuid3(uuid.NAMESPACE_DNS, 'Yidhra'),
                discord=UserDiscord(),
                hash=generate_password_hash(password, rounds=10),
                name=mail,
            )
            newUser.save()
    except Exception as e:
        msg = f'User Creation KO (mail:{mail}) [{e}]'
        logger.error(msg)
    else:
        subject = '[🐒&🐖] Bienvenue chez le Singouins !'
        token = generate_confirmation_token(mail)
        url = f'{API_URL}/auth/confirm/{token}'
        body = open(f"{DATA_PATH}/registered.html", "r").read()

        if send(
            mail,
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
                    "user": UserDocument.objects.get(name=mail).to_mongo().to_dict(),
                }
            ), 201
        else:
            msg = "User successfully added | mail KO"
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                    "user": UserDocument.objects.get(name=mail).to_mongo().to_dict(),
                }
            ), 200
