# -*- coding: utf8 -*-

import datetime
import random

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Corpse import CorpseDocument
from mongo.models.Highscore import HighscoreDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from routes._decorators import belongs, exists
from routes.mypc.action.profession._tools import (
    probabilistic_binary,
    profession_gain,
    profession_scaled,
    )
from utils.redis import get_pa
from variables import rarity_array

#
# Profession.skinning specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'skinning'


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST ../profession/skinning/<uuid:resourceuuid>
@jwt_required()
# Custom decorators
@exists.creature
@belongs.creature_in_instance
@exists.pa(red=PA_COST_RED, blue=PA_COST_BLUE, consume=True)
def skinning(creatureuuid, resourceuuid):

    # Check if the corpse exists
    try:
        Corpse = CorpseDocument.objects(_id=resourceuuid).get()
    except CorpseDocument.DoesNotExist:
        msg = f'{g.h} CorpseUUID({resourceuuid}) NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if abs(Corpse.x - g.Creature.x) > 1 or abs(Corpse.y - g.Creature.y) > 1:
        msg = f'{g.h} CorpseUUID({resourceuuid}) not in range'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    Profession = ProfessionDocument.objects(_id=creatureuuid).get()

    # We update the Profession score
    profession_gain(g.Creature.id, PROFESSION_NAME, Profession.skinning)

    # To check what's going to be created
    resource_skinned = {'skin': 0, 'meat': 0}

    for resource in resource_skinned:
        # We calculate the total quantity
        varx = rarity_array['creature'].index(Corpse.rarity)   # between 0 and 5
        vary = 0                                               # between 0 and 4
        varz = probabilistic_binary(g.Creature.stats.total.r)  # between 0 and 1

        # We tune a bit vary to have a better distribution
        for _ in range(profession_scaled(Profession.skinning)):
            vary += random.randint(1, 2)

        resource_skinned[resource] = varx + vary + varz
        logger.trace(f"{g.h} Roll for {PROFESSION_NAME}/{resource}: {varx} + {vary} + {varz} == {resource_skinned[resource]}")  # noqa: E501

    # We set the HighScores
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__meat__obtained': resource_skinned['meat'],
        'inc__internal__skin__obtained': resource_skinned['skin'],
        "set__updated": datetime.datetime.utcnow(),
        }
    HighscoreDocument.objects(_id=g.Creature.id).update_one(**highscores_update_query)

    # We add the resources in the Satchel
    satchel_update_query = {
        "inc__resource__meat": resource_skinned['meat'],
        "inc__resource__skin": resource_skinned['skin'],
        "set__updated": datetime.datetime.utcnow(),
        }
    SatchelDocument.objects(_id=creatureuuid).update_one(**satchel_update_query)

    # Little snippet to check amount of resources // slots
    # slots_used = 0
    # satchel = r.json().get(f'satchels:{g.Creature.id}')
    # for resource_data in satchel['resources'].values():
    #    for resource in resource_data.values():
    #        slots_used += resource

    try:
        Corpse.delete()
    except Exception as e:
        logger.error(f'{g.h} Corpse destroy KO (failed or no corpse was deleted) [{e}]')
    else:
        logger.trace(f'{g.h} Corpse destroy OK')

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
                        "count": resource_skinned['meat'],
                        "material": 'meat',
                        "rarity": None,
                        },
                    {
                        "count": resource_skinned['skin'],
                        "material": 'skin',
                        "rarity": None,
                        },
                    ],
                "inventory": "HARDCODED_VALUE",
            }
        }
    ), 200
