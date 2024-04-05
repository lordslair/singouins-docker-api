# -*- coding: utf8 -*-

from datetime import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from math import floor
from random import choices, randint

from nosql.models.RedisCorpse import RedisCorpse
from nosql.models.RedisEvent import RedisEvent
from nosql.models.RedisPa import RedisPa
from nosql.models.RedisStats import RedisStats

from mongo.models.Highscore import HighscoreDocument

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_creature_pa,
    check_creature_profession,
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
@check_creature_profession(PROFESSION_NAME)
def skinning(creatureuuid, resourceuuid):
    # We load a lot of Redis Objects for later
    Stats = RedisStats(creatureuuid=g.Creature.id)

    # Check if the corpse exists
    if RedisCorpse(corpseuuid=resourceuuid).exists():
        Corpse = RedisCorpse(corpseuuid=resourceuuid).load()
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

    # We calculate the amount of Profession points acquired
    if 100 <= g.Profession.skinning:         # 100+
        pass
    elif 75 <= g.Profession.skinning < 100:  # 75-99
        count = choices([0, 1], weights=[70, 30])[0]
    elif 50 <= g.Profession.skinning < 75:   # 50-74
        count = choices([0, 1], weights=[60, 40])[0]
    elif 25 <= g.Profession.skinning < 50:   # 25-49
        count = choices([0, 1], weights=[50, 50])[0]
    elif g.Profession.skinning < 25:         # 0-24
        count = 1
    # We INCR the Profession accordingly
    if count >= 1:
        g.Profession.incr(PROFESSION_NAME, count=count)

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
        f' + {floor(g.Profession.skinning/20)}D3'
        f' + {floor((Stats.p + Stats.r) / 2 / 100)}'
        )
    # We roll for skin
    skin_qty = rarity_array['creature'].index(Corpse.rarity) \
        + floor(g.Profession.skinning/20) * randint(1, 3) \
        + floor((Stats.p + Stats.r) / 2 / 100)
    # We roll for meat
    meat_qty = rarity_array['creature'].index(Corpse.rarity) \
        + floor(g.Profession.skinning/20) * randint(1, 3) \
        + floor((Stats.p + Stats.r) / 2 / 100)

    # We set the HighScores
    HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    #
    HighScores.update_one(inc__profession__tanning=1)
    HighScores.update_one(inc__internal__skin__obtained=skin_qty)
    HighScores.update_one(inc__internal__meat__obtained=meat_qty)
    #
    HighScores.update(set__updated=datetime.utcnow())

    # We prepare Event message
    if skin_qty > 0 or meat_qty > 0:
        action_text = 'Skinned something !'
    else:
        action_text = 'Skinned nothing.'
    # We create the Creature Event
    RedisEvent().new(
        action_src=g.Creature.id,
        action_dst=None,
        action_type=f'action/profession/{PROFESSION_NAME}',
        action_text=action_text,
        action_ttl=30 * 86400
        )

    # We add the resources in the Satchel
    # Satchel.incr('skin', count=skin_qty)
    # Satchel.incr('meat', count=meat_qty)

    # Little snippet to check amount of resources // slots
    # slots_used = 0
    # satchel = r.json().get(f'satchels:{g.Creature.id}')
    # for resource_data in satchel['resources'].values():
    #    for resource in resource_data.values():
    #        slots_used += resource

    # We consume the PA
    RedisPa(creatureuuid=creatureuuid).consume(bluepa=PA_COST_BLUE, redpa=PA_COST_RED)

    if Corpse.destroy():
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
