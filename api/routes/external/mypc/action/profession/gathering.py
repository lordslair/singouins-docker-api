# -*- coding: utf8 -*-

from datetime import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from random import choices

from mongo.models.Highscore import HighscoreDocument
from mongo.models.Resource import ResourceDocument

from nosql.models.RedisPa import RedisPa

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_creature_pa,
    )
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
# API: POST ../profession/gathering/<uuid:resourceuuid>
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

    # We calculate the amount of Profession points acquired
    # You CANNOT get more than 1 point
    # You CAN have 0 points if you are already skilled enough and learned nothing
    if 100 <= g.Profession.gathering:         # 100+
        pass
    elif 75 <= g.Profession.gathering < 100:  # 75-99
        count = choices([0, 1], weights=[70, 30])[0]
    elif 50 <= g.Profession.gathering < 75:   # 50-74
        count = choices([0, 1], weights=[60, 40])[0]
    elif 25 <= g.Profession.gathering < 50:   # 25-49
        count = choices([0, 1], weights=[50, 50])[0]
    elif g.Profession.gathering < 25:         # 0-24
        count = 1
    # We INCR the Profession accordingly
    if count >= 1:
        g.Profession.incr(PROFESSION_NAME, count=count)

    """
    We cap possible gathered resources to Resource.rarity
    rarity_array = [
        'Broken',
        'Common',
        'Uncommon',
        'Rare',
        'Epic',
        'Legendary',
    ]
    """
    local_rarity_array = rarity_array.copy()
    while len(local_rarity_array) > rarity_array.index(Resource.rarity) + 1:
        local_rarity_array.pop(rarity_array.index(Resource.rarity) + 1)
    """
    After this point, as exemple
    if the Resource.rarity == 'Rare':
        local_rarity_array = ['Broken', 'Common', 'Uncommon', 'Rare']
    """

    # We find out quantity and quality/rarity
    # If a resource is high quality, the Player will have less quantity
    rarity = choices(rarity_array, k=1)[0]
    quantity = max(
        0,
        1 + round(g.Profession.gathering/20 - rarity_array.index(rarity))
        )

    # We set the HighScores
    HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    #
    HighScores.update_one(inc__profession__gathering=1)
    HighScores.update_one(inc__internal__ore__obtained=quantity)
    #
    HighScores.update(set__updated=datetime.utcnow())

    # We add the resources in the Wallet
    #
    # TODO
    #

    # We consume the PA
    RedisPa(creatureuuid=creatureuuid).consume(bluepa=PA_COST_BLUE, redpa=PA_COST_RED)

    # We're done
    msg = f'{g.h} Profession ({PROFESSION_NAME}) Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "pa": RedisPa(creatureuuid=creatureuuid).as_dict(),
                "resource": {
                    "count": quantity,
                    "material": Resource.material,
                    "rarity": rarity,
                },
            }
        }
    ), 200
