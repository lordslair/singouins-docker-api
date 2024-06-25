# -*- coding: utf8 -*-

from flask import jsonify
from loguru import logger

from utils.token import confirm_token
from mongo.models.User import UserDocument


# API: GET /auth/confirm/{token}
def confirm(token):
    username = confirm_token(token)
    if username:
        try:
            User = UserDocument.objects(name=username).first()
            User.active = True
            User.save()
        except Exception as e:
            msg = f'User confirmation KO (username:{username}) [{e}]'
            logger.error(msg)
        else:
            msg = f'User confirmation OK (username:{username})'
            logger.trace(msg)
    else:
        msg = "Confirmation link invalid or has expired"
        logger.warning(msg)

    # Finally
    return jsonify(
        {
            "msg": msg,
        }
    ), 200
