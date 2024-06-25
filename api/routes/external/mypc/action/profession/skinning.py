# -*- coding: utf8 -*-


import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from math import floor
from random import choices, randint

from mongo.models.Corpse import CorpseDocument
from mongo.models.Highscore import HighscoreDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from nosql.models.RedisPa import RedisPa

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_creature_pa,
    )
from variables import rarity_array

#
# Profession.skinning specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'skinning'
"""
This Profession HAVE TO be executed in Instance.
"""


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST ../profession/skinning/<uuid:resourceuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
def skinning(creatureuuid, resourceuuid):
    # Check if the corpse exists
    if CorpseDocument.objects(_id=resourceuuid):
        Corpse = CorpseDocument.objects(_id=resourceuuid).get
    else:
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
        msg = f'{g.h} Corpse not in range'
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
    if 100 <= Profession.skinning:         # 100+
        pass
    elif 75 <= Profession.skinning < 100:  # 75-99
        count = choices([0, 1], weights=[70, 30])[0]
    elif 50 <= Profession.skinning < 75:   # 50-74
        count = choices([0, 1], weights=[60, 40])[0]
    elif 25 <= Profession.skinning < 50:   # 25-49
        count = choices([0, 1], weights=[50, 50])[0]
    elif Profession.skinning < 25:         # 0-24
        count = 1
    # We INCR the Profession accordingly
    if count >= 1:
        profession_update_query = {
            f'inc__{PROFESSION_NAME}': count,
            "set__updated": datetime.datetime.utcnow(),
            }
        Profession.update(**profession_update_query)

    """
    * Quantity skinned depends on Profession, Corpse.rarity, and Stats

    NB:
    Profession.skinning/20    is between 0 and 5
    (Stats.p + Stats.r)/2/100 is between 0 and 2
    Complete skinning result  is between 0 and (5 + 5D3 + 2)

    # skin/peau
    * Small :  0 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Medium : 1 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Big :    2 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Unique : 3 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Boss :   4 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * God :    5 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100

    # Viande/Meat
    * Small :  0 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Medium : 1 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Big :    2 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Unique : 3 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * Boss :   4 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    * God :    5 + (Profession.skinning/20) D3 + (Stats.p + Stats.r)/2/100
    """

    """ We roll twice the same formula, just to have different results for skin and meat """
    logger.trace(
        f"{g.h} Roll for skinning: {rarity_array['creature'].index(Corpse.rarity)}"
        f' + {floor(Profession.skinning/20)}D3'
        f' + {floor((g.Creature.stats.total.p + g.Creature.stats.total.r) / 2 / 100)}'
        )
    # We roll for skin
    skin_qty = rarity_array['creature'].index(Corpse.rarity) \
        + floor(Profession.skinning/20) * randint(1, 3) \
        + floor((g.Creature.stats.total.p + g.Creature.stats.total.r) / 2 / 100)
    # We roll for meat
    meat_qty = rarity_array['creature'].index(Corpse.rarity) \
        + floor(Profession.skinning/20) * randint(1, 3) \
        + floor((g.Creature.stats.total.p + g.Creature.stats.total.r) / 2 / 100)

    # We set the HighScores
    HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__meat__obtained': meat_qty,
        'inc__internal__skin__obtained': skin_qty,
        "set__updated": datetime.datetime.utcnow(),
        }
    HighScores.update(**highscores_update_query)

    # We add the resources in the Satchel
    Satchel = SatchelDocument.objects(_id=creatureuuid).get()
    satchel_update_query = {
        "inc__resource__meat": meat_qty,
        "inc__resource__skin": skin_qty,
        "set__updated": datetime.datetime.utcnow(),
        }
    Satchel.update(**satchel_update_query)

    # Little snippet to check amount of resources // slots
    # slots_used = 0
    # satchel = r.json().get(f'satchels:{g.Creature.id}')
    # for resource_data in satchel['resources'].values():
    #    for resource in resource_data.values():
    #        slots_used += resource

    # We consume the PA
    RedisPa(creatureuuid=creatureuuid).consume(bluepa=PA_COST_BLUE, redpa=PA_COST_RED)

    if Corpse.delete():
        pass
    else:
        msg = f'{g.h} Corpse destroy KO'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We're done
    msg = f'{g.h} Profession ({PROFESSION_NAME}) Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "pa": RedisPa(creatureuuid=creatureuuid).as_dict(),
                "resource": [
                    {
                        "count": skin_qty,
                        "material": 'skin',
                        "rarity": 'common',
                        },
                    {
                        "count": meat_qty,
                        "material": 'meat',
                        "rarity": 'common',
                        },
                    ],
                "inventory": "HARDCODED_VALUE",
            }
        }
    ), 200
