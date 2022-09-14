# -*- coding: utf8 -*-

from flask                  import jsonify, request
from flask_bcrypt           import check_password_hash
from flask_jwt_extended     import (jwt_required,
                                    create_access_token,
                                    create_refresh_token,
                                    get_jwt_identity)
from loguru                 import logger

from mysql.methods.fn_user import (fn_forgot_password,
                                   fn_user_add,
                                   fn_user_confirm,
                                   fn_user_del,
                                   fn_user_get)
from utils.mail            import send
from utils.token           import (confirm_token,
                                   generate_confirmation_token)

from variables             import (API_URL,
                                   DATA_PATH,
                                   DISCORD_URL)


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

    if fn_user_get(username):
        pass_db    = fn_user_get(username).hash
        pass_check = check_password_hash(pass_db, password)
    else:
        pass_check = None

    if not fn_user_get(username) or not pass_check:
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

    code = fn_user_add(mail, password)
    if code == 201:
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
            ), code
        else:
            msg = "User successfully added | mail KO"
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), code
    elif code == 409:
        msg = "User or Email already exists"
        logger.trace(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), code
    else:
        msg = "Oops!"
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 422


# API: GET /auth/confirm/{token}
def auth_confirm(token):
    username = confirm_token(token)
    if username:
        if fn_user_confirm(username):
            msg = f'User Confirmation OK (username:{username})'
            logger.trace(msg)
        else:
            msg = f'User Confirmation KO (username:{username})'
            logger.error(msg)
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

    code = fn_user_del(username)
    if code == 200:
        msg = "User successfully deleted"
        logger.trace(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), code
    if code == 404:
        msg = "Bad username"
        logger.warning(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), code
    else:
        msg = "Oops!"
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 422


# API: POST /auth/forgotpassword
def auth_forgotpassword():
    if not request.is_json:
        return jsonify(
            {
                "msg": "Missing JSON in request",
            }
        ), 400

    mail             = request.json.get('mail', None)
    (code, password) = fn_forgot_password(mail)

    if code == 200:
        subject = '[🐒&🐖] Mot de passe oublié'
        body    = open(f"{DATA_PATH}/forgot_password.html", "r").read()
        if send(mail,
                subject,
                body.format(urllogo='[INSERT LOGO HERE]',
                            password=password,
                            urldiscord=DISCORD_URL)):
            msg = "Password successfully replaced | mail OK"
            logger.trace(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), code
        else:
            msg = "Password successfully replaced | mail KO"
            logger.warning(msg)
            return jsonify(
                {
                    "msg": msg,
                }
            ), code
    else:
        msg = "Oops!"
        logger.error(msg)
        return jsonify(
            {
                "msg": msg,
            }
        ), 422


# API: POST /auth/infos
@jwt_required()
def auth_infos():
    msg = "User Query OK"
    logger.trace(msg)
    # Access the identity of the current user with get_jwt_identity
    return jsonify(logged_in_as=get_jwt_identity()), 200
