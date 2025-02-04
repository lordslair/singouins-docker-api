# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from random import choices

from mongo.models.Highscore import HighscoreDocument
from mongo.models.Satchel import SatchelDocument

from routes._decorators import exists
from routes.mypc.action.profession._tools import profession_gain
from utils.redis import get_pa

#
# Profession.tanning specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'tanning'


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST /mypc/<uuid:creatureuuid>/action/profession/tanning
@jwt_required()
# Custom decorators
@exists.creature
@exists.pa(red=PA_COST_RED, blue=PA_COST_BLUE, consume=True)
def tanning(creatureuuid):
    Satchel = SatchelDocument.objects(_id=creatureuuid).get()

    if Satchel.resource.skin < 10:
        msg = f'{g.h} Not enough resource.skin to tan.'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": {
                    "satchel": Satchel.to_mongo(),
                },
            }
        ), 200

    # To check what's going to be created
    resource_tanned = {'fur': 0, 'leather': 0}

    # We roll to know if we will generate leather or fur
    resource_type = choices(['fur', 'leather'], weights=[50, 50])[0]
    logger.debug(f'{g.h} Roll for tanning: a {resource_type} has been tanned')
    # We increment the quantity
    resource_tanned[resource_type] += 1

    # We set the HighScores
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__fur__obtained': resource_tanned['fur'],
        'inc__internal__leather__obtained': resource_tanned['leather'],
        "set__updated": datetime.datetime.utcnow(),
        }
    HighscoreDocument.objects(_id=g.Creature.id).update(**highscores_update_query)

    # We add the resources in the Satchel
    satchel_update_query = {
        "inc__resource__fur": resource_tanned['fur'],
        "inc__resource__leather": resource_tanned['leather'],
        "inc__resource__skin": - 10,
        "set__updated": datetime.datetime.utcnow(),
        }
    SatchelDocument.objects(_id=creatureuuid).update_one(**satchel_update_query)

    # We update the Profession score
    profession_gain(g.Creature.id, PROFESSION_NAME)

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
