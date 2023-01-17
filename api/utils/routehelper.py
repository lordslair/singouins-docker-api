# -*- coding: utf8 -*-

from flask                      import jsonify
from loguru                     import logger

from nosql.models.RedisUser     import RedisUser

from variables                  import API_INTERNAL_TOKEN


def request_internal_token_check(request):
    bearer = f'Bearer {API_INTERNAL_TOKEN}'
    try:
        if request.headers.get('Authorization') != bearer:
            msg = '[API] Token not authorized'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 403
    except Exception as e:
        logger.error(f'[API] Token validation failed [{e}]')
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        return True


def request_json_check(request):
    try:
        if not request.is_json:
            msg = '[API] Missing JSON in request'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 400
    except Exception as e:
        logger.error(f'[API] JSON validation failed [{e}]')
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        return True


def creature_check(Creature, username=None):
    try:
        # We check that The Creature is found
        # Or it's useless to continue
        if Creature is None or Creature is False:
            msg = '[Creature.id:None] Creature NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        # If the Creature is found, and if a User is provided
        # We check if the User owns the Creature
        if username is not None:
            User = RedisUser(username=username)
            if Creature.account != User.id:
                msg = (
                    f'[Creature.id:{Creature.id}] Creature/User mismatch '
                    f'(username:{User.name})'
                    )
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 409
    except Exception:
        pass
    else:
        return f'[Creature.id:{Creature.id}]'
