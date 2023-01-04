# -*- coding: utf8 -*-

import string

from flask                  import jsonify, request
from flask_bcrypt           import check_password_hash, generate_password_hash
from flask_jwt_extended     import (jwt_required,
                                    create_access_token,
                                    create_refresh_token,
                                    get_jwt_identity)
from loguru                 import logger
from random                 import choice

from utils.mail            import send
from utils.token           import (confirm_token,
                                   generate_confirmation_token)

from variables             import (API_URL,
                                   DATA_PATH,
                                   DISCORD_URL)


from nosql.models.RedisUser   import RedisUser


#
# Routes /auth
#
# API: POST /auth/login
def auth_login():
    if not request.is_json:
        return jsonify(
            {
                "msg": "Missing JSON in request",
            }
        ), 400

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

    User = RedisUser().get(username)
    if not User or not check_password_hash(User.hash, password):
        msg = "Bad username or password"
        logger.warning(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 401

    # Identity can be any data that is json serializable
    msg = "Access Token Query OK"
    logger.trace(msg)
    return jsonify(
        {
            'access_token': create_access_token(identity=username),
            'refresh_token': create_refresh_token(identity=username)
        }
    ), 200


# API: POST /auth/refresh
@jwt_required(refresh=True)
def auth_refresh():
    msg = "Refresh Token Query OK"
    logger.trace(msg)
    return jsonify(
        {
            'access_token': create_access_token(identity=get_jwt_identity())
        }
    ), 200


# API: POST /auth/register
def auth_register():
    if not request.is_json:
        return jsonify(
            {
                "msg": "Missing JSON in request",
            }
        ), 400

    password = request.json.get('password', None)
    mail     = request.json.get('mail', None)
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
    h = '[User.id:None]'  # Header for logging
    try:
        User = RedisUser().get(mail)
    except Exception as e:
        msg = f'{h} User Query KO (mail:{mail}) [{e}]'
        logger.error(msg)
    else:
        if User:
            msg = f"User already exists (mail:{mail})"
            logger.trace(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 409

    User = RedisUser().new(
        mail,
        generate_password_hash(password, rounds=10),
        )

    if User:
        subject = '[🐒&🐖] Bienvenue chez le Singouins !'
        token   = generate_confirmation_token(mail)
        url     = f'{API_URL}/auth/confirm/{token}'
        body    = open(f"{DATA_PATH}/registered.html", "r").read()
        if send(mail,
                subject,
                body.format(urllogo='[INSERT LOGO HERE]',
                            urlconfirm=url,
                            urldiscord=DISCORD_URL)):
            msg = "User successfully added | mail OK"
            logger.trace(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 201
        else:
            msg = "User successfully added | mail KO"
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 200


# API: GET /auth/confirm/{token}
def auth_confirm(token):
    username = confirm_token(token)
    if username:
        try:
            User = RedisUser().get(username)
            User.active = True
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


# API: DELETE /auth/delete
@jwt_required()
def auth_delete():
    if not request.is_json:
        return jsonify(
            {
                "msg": "Missing JSON in request",
            }
        ), 400

    username     = request.json.get('username', None)
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
        RedisUser().destroy(username)
    except Exception as e:
        msg = f'User deletion KO (username:{username}) [{e}]'
        logger.error(msg)
    else:
        msg = f'User deletion OK (username:{username})'
        logger.trace(msg)

    return jsonify(
        {
            "msg": msg,
        }
    ), 200


# API: POST /auth/forgotpassword
def auth_forgotpassword():
    if not request.is_json:
        return jsonify(
            {
                "msg": "Missing JSON in request",
            }
        ), 400

    mail = request.json.get('mail', None)
    User = RedisUser().get(mail)

    # We setup necessary to generate a new random password
    length    = 12
    letterset = string.ascii_letters + string.digits
    password  = ''.join((choice(letterset) for i in range(length)))

    try:
        User.hash = generate_password_hash(password, rounds=10)
    except Exception as e:
        msg = f"Password replacement KO [{e}]"
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 200
    else:
        if User.hash.decode("utf-8") != RedisUser().get(mail).hash:
            # If hashes are != we screwed up the update
            msg = "Password replacement KO"
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), 200

        # Everything went fine
        try:
            subject = '[🐒&🐖] Mot de passe oublié'
            body    = open(f"{DATA_PATH}/forgot_password.html", "r").read()

            send(
                mail,
                subject,
                body.format(
                    urllogo='[INSERT LOGO HERE]',
                    password=password,
                    urldiscord=DISCORD_URL,
                    ),
                )
        except Exception as e:
            msg = f"Password replacement OK | mail KO [{e}]"
            logger.error(msg)
        else:
            msg = "Password replacement OK | mail OK"
            logger.trace(msg)

        return jsonify(
            {
                "msg": msg,
            }
        ), 200


# API: POST /auth/infos
@jwt_required()
def auth_infos():
    msg = "User Query OK"
    logger.trace(msg)
    # Access the identity of the current user with get_jwt_identity
    return jsonify(logged_in_as=get_jwt_identity()), 200
