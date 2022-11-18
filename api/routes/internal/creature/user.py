# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisUser     import RedisUser

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/user
def creature_user(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    try:
        User = RedisUser().search(
            field='id',
            # GruikFix
            # We need to do the replace as the [-] is seen as separator
            # Would need to baclslash it, but easier that way
            query=Creature.account.replace('-', ' ')
            )
    except Exception as e:
        msg = f'{h} User Query KO (accountid:{Creature.account}) [{e}]'
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
            msg = f'{h} User Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "user": User,
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} User Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
