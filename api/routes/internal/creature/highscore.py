# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisHS       import RedisHS

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/creature/{creatureid}/highscore
def creature_highscore_get(creatureid):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    # We fetch the HighScores
    try:
        hs = RedisHS(Creature)
    except Exception as e:
        msg = f'{h} HighScores Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if hs:
            msg = f'{h} HighScores Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "highscore": hs._asdict(),
                        "creature": Creature._asdict(),
                        },
                }
            ), 200
        else:
            msg = f'{h} HighScores Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
