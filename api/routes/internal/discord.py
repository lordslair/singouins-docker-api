# -*- coding: utf8 -*-

from flask                     import jsonify, request
from loguru                    import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisUser    import RedisUser

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    request_json_check,
    )

#
# Routes /internal
#


# /internal/discord/*
# /internal/discord/link
def discord_link():
    request_internal_token_check(request)
    request_json_check(request)

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
        User = RedisUser().get(usermail)
        User.d_name = discordname
        User.d_ack = True
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
        if User:
            msg = f'Query OK (discordname:{discordname})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": User._asdict(),
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
    request_internal_token_check(request)
    request_json_check(request)

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

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    User = RedisUser().search(field='d_name', query=discordname)
    if User is None:
        msg = f'{h} Query KO - NotFound (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if Creature.account == User.id:
        # The Discord user owns the Creature
        msg = f'{h} Query OK (discordname:{discordname})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "user": User._asdict(),
                    "creature": Creature._asdict(),
                    },
            }
        ), 200
    else:
        # The Discord user do NOT own the Creature
        msg = f'{h} Query KO - Not Yours (discordname:{discordname}'
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
    request_internal_token_check(request)
    request_json_check(request)

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

    if discordname == 'None':
        # If we are here, means the request is weird
        # And probably sent by someone not linked
        msg = f'Discordname should be defined (discordname:{discordname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Users = RedisUser().search(field='d_name', query=discordname)
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
        if len(Users) == 0:
            msg = f'Query KO - NotFound (discordname:{discordname})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            User = Users[0]

    try:
        account = User['id'].replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@account:{account}')
    except Exception as e:
        msg = f'Query KO (userid:{User.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'Query OK (discordname:{discordname})'
        logger.debug(msg)
        if len(Creatures) > 0:
            code = 200
        else:
            code = 404

        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creatures,
            }
        ), code


# /internal/discord/user
def discord_user():
    request_internal_token_check(request)
    request_json_check(request)

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
        Users = RedisUser().search(field='d_name', query=discordname)
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
        if len(Users) == 0:
            msg = f'Query KO - NotFound (discordname:{discordname})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 404
        else:
            User = Users[0]
            msg = f'Query OK (discordname:{discordname})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": User,
                }
            ), 200
