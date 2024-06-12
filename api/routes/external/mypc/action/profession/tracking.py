# -*- coding: utf8 -*-

from datetime import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Highscore import HighscoreDocument

from nosql.models.RedisEffect import RedisEffect
from nosql.models.RedisPa import RedisPa

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_creature_pa,
    )

#
# Profession.tracking specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
DURATION = 3600
DISTANCE = 3
PROFESSION_NAME = 'tracking'


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST ../profession/tracking
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
def track(creatureuuid):
    # A tracking extends Creature view for X tiles for Y seconds
    # We need to add the Effect for that
    # The real job is done in /view

    RedisEffect(creatureuuid=g.Creature.id).new(
        duration_base=DURATION,
        extra=None,
        instanceuuid=g.Creature.instance,
        name=None,
        source=None,
    )

    # We set the HighScores
    HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        "set__updated": datetime.datetime.utcnow(),
        }
    HighScores.update(**highscores_update_query)

    # We consume the PA
    RedisPa(creatureuuid=creatureuuid).consume(
        bluepa=PA_COST_BLUE,
        redpa=PA_COST_RED,
    )

    msg = f'{g.h} Profession Query OK (tracking)'
    logger.debug(msg)

    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "pa": RedisPa(creatureuuid=creatureuuid).as_dict(),
                "effects": [],
            }
        }
    ), 200
