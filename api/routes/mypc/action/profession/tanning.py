# -*- coding: utf8 -*-

from datetime import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from random import choices

from mongo.models.Highscore import HighscoreDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from utils.decorators import (
    check_creature_exists,
    check_creature_pa,
    )
from utils.redis import get_pa, consume_pa

#
# Profession.tanning specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'tanning'
"""
This Profession can be executed in WORLD, we do not check:
    @check_creature_in_instance
"""


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST ../profession/tanning/<int:quantity>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
def tanning(creatureuuid, quantity):
    Satchel = SatchelDocument.objects(_id=creatureuuid).get()

    # Check we have enough to tan
    if Satchel.resouce.skin < quantity:
        msg = f'{g.h} Not enough skin to tan this amount.'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    Profession = ProfessionDocument.objects(_id=creatureuuid).get()

    # We calculate the amount of Profession points acquired
    if 100 <= Profession.tanning:         # 100+
        pass
    elif 75 <= Profession.tanning < 100:  # 75-99
        count = choices([0, 1], weights=[70, 30])[0]
    elif 50 <= Profession.tanning < 75:   # 50-74
        count = choices([0, 1], weights=[60, 40])[0]
    elif 25 <= Profession.tanning < 50:   # 25-49
        count = choices([0, 1], weights=[50, 50])[0]
    elif Profession.tanning < 25:         # 0-24
        count = 1
    # We INCR the Profession accordingly
    if count >= 1:
        profession_update_query = {
            f'inc__{PROFESSION_NAME}': count,
            "set__updated": datetime.datetime.utcnow(),
            }
        Profession.update(**profession_update_query)

    """
    * Quantity tanned depends on Profession, and Stats

    NB:
    Profession.tanning/20   is between 0 and 5
    """

    # We will do all these rolls FOR EACH tanned skin
    resource_tanned = {
        'fur': 0,
        'leather': 0,
    }

    for skin in range(quantity):
        # We roll to know if we will generate leather or fur
        resource_type = choices(['fur', 'leather'], weights=[50, 50])[0]
        logger.debug(f'{g.h} Roll for tanning: a {resource_type} has been tanned')
        # We increment the quantity
        resource_tanned[resource_type] += 1
    logger.debug(f'{g.h} resource_tanned: {resource_tanned}')

    # We set the HighScores
    HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__fur__obtained': resource_tanned['fur'],
        'inc__internal__leather__obtained': resource_tanned['leather'],
        "set__updated": datetime.datetime.utcnow(),
        }
    HighScores.update(**highscores_update_query)

    # We add the resources in the Satchel
    satchel_update_query = {
        "inc__resource__fur": resource_tanned['fur'],
        "inc__resource__leather": resource_tanned['leather'],
        "inc__resource__skin": -quantity,
        "set__updated": datetime.datetime.utcnow(),
        }
    Satchel.update(**satchel_update_query)

    # We consume the PA
    consume_pa(creatureuuid=creatureuuid, bluepa=PA_COST_BLUE, redpa=PA_COST_RED)

    # We're done
    msg = f'{g.h} Profession ({PROFESSION_NAME}) Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "pa": get_pa(creatureuuid=g.Creature.id),
                "resource": [
                    {
                        "count": resource_tanned['fur'],
                        "material": 'fur',
                        "rarity": None,
                        },
                    {
                        "count": resource_tanned['leather'],
                        "material": 'leather',
                        "rarity": None,
                        },
                    ],
            }
        }
    ), 200
