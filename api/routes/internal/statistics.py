# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisHS       import RedisHS

from utils.routehelper          import (
    request_internal_token_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: GET /internal/statistics/highscores
def statistics_highscores():
    request_internal_token_check(request)
    h = '[Creature.id:None]'

    """
    Here we are to rebuild the TOP1 Player for all of the HighScores
    We will keep the computated results in Redis for 300 seconds
    """

    # We fetch the HighScores
    try:
        maxhs_score = dict()
        HighScores = RedisHS().search(query='*')
        if len(HighScores) > 0:
            for HighScore in HighScores:
                for key, val in HighScore.items():
                    if key == 'payload':
                        pass
                    elif key == 'id':
                        creatureuuid = val
                    else:
                        if key not in maxhs_score:
                            maxhs_score[key] = {
                                "value": 0,
                                "creature": None,
                                }

                        if val and val >= maxhs_score[key]['value']:
                            maxhs_score[key]['value'] = val
                            maxhs_score[key]['creature'] = creatureuuid

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
        msg = f'{h} HighScores Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": maxhs_score,
            }
        ), 200
