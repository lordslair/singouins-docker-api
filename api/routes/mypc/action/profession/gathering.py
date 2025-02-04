# -*- coding: utf8 -*-

import datetime
import random

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Highscore import HighscoreDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Resource import ResourceDocument
from mongo.models.Satchel import SatchelDocument

from routes.mypc.action.profession._tools import (
    probabilistic_binary,
    profession_gain,
    profession_scaled,
    )
from utils.redis import get_pa
from variables import rarity_array

#
# Profession.gathering specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 4
PROFESSION_NAME = 'gathering'


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST /mypc/<uuid:creatureuuid>/action/profession/gathering/<uuid:resourceuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
def gathering(creatureuuid, resourceuuid):
    # Check if the resource exists
    if ResourceDocument.objects(_id=resourceuuid):
        Resource = ResourceDocument.objects(_id=resourceuuid).get()
    else:
        msg = f'{g.h} ResourceUUID({resourceuuid}) NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    Profession = ProfessionDocument.objects(_id=creatureuuid).get()

    # We calculate the total quantity
    varx = 5 - rarity_array['item'].index(Resource.rarity)  # between 0 and 5
    vary = 0                                                # between 0 and 8
    varz = probabilistic_binary(g.Creature.stats.total.m)   # between 0 and 1

    # We tune a bit vary to have a better distribution
    for _ in range(profession_scaled(Profession.skinning)):
        vary += random.randint(1, 2)

    quantity = varx + vary + varz
    logger.trace(f"{g.h} Roll for {PROFESSION_NAME}: {varx} + {vary} + {varz} == {quantity}")  # noqa: E501

    # We update the Profession score
    profession_gain(g.Creature.id, PROFESSION_NAME, Profession.gathering)

    # We set the HighScores
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__ore__obtained': quantity,
        "set__updated": datetime.datetime.utcnow(),
        }
    HighscoreDocument.objects(_id=g.Creature.id).update_one(**highscores_update_query)

    # We add the resources in the Satchel
    Satchel = SatchelDocument.objects(_id=creatureuuid).get()
    Satchel.update(
        inc__resource__ore=quantity,
        set__updated=datetime.datetime.utcnow()
    )
    Satchel.reload()

    # We delete the Resource in DB
    try:
        Resource.delete()
    except Exception as e:
        logger.error(f'{g.h} Resource destroy KO (failed or no resource was deleted) [{e}]')
    else:
        logger.trace(f'{g.h} Resource destroy OK')

    # We're done
    msg = f'{g.h} Profession ({PROFESSION_NAME}) Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "pa": get_pa(creatureuuid=g.Creature.id),
                "resource": [{
                    "count": quantity,
                    "material": 'ore',
                    "rarity": None,
                }],
            }
        }
    ), 200
