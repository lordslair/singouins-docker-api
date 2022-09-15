# -*- coding: utf8 -*-

from flask                     import jsonify, request
from loguru                    import logger

from mysql.methods.fn_user     import (fn_user_get_from_discord,
                                       fn_user_link_from_discord)
from mysql.methods.fn_creature import (fn_creature_get_all,
                                       fn_creature_get)

from variables                 import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/discord/*
# /internal/discord/link
def discord_link():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    discordname  = request.json.get('discordname')
    usermail     = request.json.get('usermail')

    if not isinstance(discordname, str):
        msg = f'Discordname should be a STR (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(usermail, str):
        msg = f'Usermail should be a STR (usermail:{usermail})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        user = fn_user_link_from_discord(discordname, usermail)
    except Exception as e:
        msg = f'Query KO (discordname:{discordname}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if user:
            msg = f'Query OK (discordname:{discordname})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": user,
                }
            ), 200
        else:
            msg = f'Query KO - NotFound (discordname:{discordname})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# /internal/discord/creature
def discord_creature_get_one():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    discordname = request.json.get('discordname')
    creatureid  = request.json.get('creatureid')

    if not isinstance(discordname, str):
        msg = f'Discordname should be a STR (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(creatureid, int):
        msg = f'Creature ID should be a INT (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    user        = fn_user_get_from_discord(discordname)
    if user is None:
        msg = f'Query KO - NotFound (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if creature.account == user.id:
        # The Discord user owns the Creature
        msg = f'Query OK (discordname:{discordname},creatureid:{creatureid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "user": user,
                    "creature": creature,
                    },
            }
        ), 200
    else:
        # The Discord user do NOT own the Creature
        msg = (f'Query KO - Not Yours '
               f'(discordname:{discordname},creatureid:{creatureid})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200


# /internal/discord/creatures
def discord_creature_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    discordname  = request.json.get('discordname')

    if not isinstance(discordname, str):
        msg = f'Discordname should be a STR (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        user = fn_user_get_from_discord(discordname)
    except Exception as e:
        msg = f'Query KO (discordname:{discordname}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if user is None:
            msg = f'Query KO - NotFound (discordname:{discordname})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    try:
        pcs = fn_creature_get_all(user.id)
    except Exception as e:
        msg = f'Query KO (userid:{user.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if pcs:
            msg = f'Query OK (discordname:{discordname})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": pcs,
                }
            ), 200
        else:
            msg = f'Query KO - NotFound (discordname:{discordname})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# /internal/discord/user
def discord_user():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    discordname  = request.json.get('discordname')

    if not isinstance(discordname, str):
        msg = f'Discordname should be a STR (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        user = fn_user_get_from_discord(discordname)
    except Exception as e:
        msg = f'Query KO (discordname:{discordname}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if user:
            msg = f'Query OK (discordname:{discordname})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": user,
                }
            ), 200
        else:
            msg = f'Query KO - NotFound (discordname:{discordname})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
