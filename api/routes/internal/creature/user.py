# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/user
def creature_user(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    try:
        Users = RedisUser().search(
            field='id',
            # GruikFix
            # We need to do the replace as the [-] is seen as separator
            # Would need to baclslash it, but easier that way
            query=Creature.account.replace('-', ' ')
            )
        User = Users[0]
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
