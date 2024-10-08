# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Highscore import HighscoreDocument

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/highscores
#
# API: GET /mypc/<uuid:creatureuuid>/highscores
@jwt_required()
# Custom decorators
@check_creature_exists
def highscores_get(creatureuuid):
    try:
        if HighscoreDocument.objects(_id=creatureuuid):
            Highscores = HighscoreDocument.objects(_id=creatureuuid).get()
        else:
            msg = f'{g.h} HighscoreDocument Query KO - DoesNotExist'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
    except Exception as e:
        msg = f'{g.h} HighscoreDocument Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": e,
            }
        ), 200
    else:
        msg = f'{g.h} HighscoreDocument Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Highscores.to_mongo(),
            }
        ), 200
