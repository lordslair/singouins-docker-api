# -*- coding: utf8 -*-

from datetime import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from math import floor
from random import choices, randint

from mongo.models.Highscore import HighscoreDocument
from nosql.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from nosql.models.RedisPa import RedisPa

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    check_creature_pa,
    )
from variables import rarity_array

#
# Profession.recycling specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'recycling'
"""
This Profession can be executed in WORLD, we do not check:
    @check_creature_in_instance
"""


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST ../profession/recycling/<uuid:itemuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
def recycling(creatureuuid, itemuuid):
    if g.Item.bearer != g.Creature.id:
        msg = f'{g.h} ItemUUID({g.Item.id}) does not belong to you'
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
    if 100 <= Profession.recycling:         # 100+
        pass
    elif 75 <= Profession.recycling < 100:  # 75-99
        count = choices([0, 1], weights=[70, 30])[0]
    elif 50 <= Profession.recycling < 75:   # 50-74
        count = choices([0, 1], weights=[60, 40])[0]
    elif 25 <= Profession.recycling < 50:   # 25-49
        count = choices([0, 1], weights=[50, 50])[0]
    elif Profession.recycling < 25:         # 0-24
        count = 1
    # We INCR the Profession accordingly
    if count >= 1:
        profession_update_query = {
            f'inc__profession__{PROFESSION_NAME}': count,
            "set__updated": datetime.datetime.utcnow(),
            }
        Profession.update(**profession_update_query)

    """
    * Quantity recycled depends on Profession, Item.rarity, and Stats

    NB:
    Profession.recycling/20   is between 0 and 5
    (Stats.p + Stats.b)/2/100 is between 0 and 2
    Complete recycling result is between 0 and (5 + 5D3 + 2)

    * Legendary : 0 + (Profession.recycling/20) D3 + (Stats.p + Stats.b)/2/100
    * Epic :      1 + (Profession.recycling/20) D3 + (Stats.p + Stats.b)/2/100
    * Rare :      2 + (Profession.recycling/20) D3 + (Stats.p + Stats.b)/2/100
    * Uncommon :  3 + (Profession.recycling/20) D3 + (Stats.p + Stats.b)/2/100
    * Common :    4 + (Profession.recycling/20) D3 + (Stats.p + Stats.b)/2/100
    * Broken :    5 + (Profession.recycling/20) D3 + (Stats.p + Stats.b)/2/100
    """

    base_qty = rarity_array['item'].index(g.Item.rarity)
    prof_d3 = floor(Profession.recycling/20)
    stat_qty = floor((g.Creature.stats.total.p + g.Creature.stats.total.b) / 2 / 100)

    # We roll the dice and calculate the total quantity
    shards_qty = base_qty + prof_d3 * randint(1, 3) + stat_qty
    logger.trace(f"{g.h} Roll for {PROFESSION_NAME}: {base_qty} + {prof_d3}D3 + {stat_qty}")
    logger.trace(f"{g.h} Roll for {PROFESSION_NAME}: {shards_qty}")

    # We set the HighScores
    HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__item__recycled': 1,
        'inc__internal__shard__obtained': shards_qty,
        "set__updated": datetime.datetime.utcnow(),
        }
    HighScores.update(**highscores_update_query)

    # We add the resources in the Satchel
    Satchel = SatchelDocument.objects(_id=creatureuuid).get()
    satchel_update_query = {
        f"inc__shard__{g.Item.rarity}": shards_qty,
        "set__updated": datetime.datetime.utcnow(),
        }
    Satchel.update(**satchel_update_query)

    # We consume the PA
    RedisPa(creatureuuid=creatureuuid).consume(bluepa=PA_COST_BLUE, redpa=PA_COST_RED)

    if g.Item.destroy():
        pass
    else:
        msg = f'{g.h} Item destroy KO'
        logger.warning(msg)

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
                        "count": shards_qty,
                        "material": 'shards',
                        "rarity": g.Item.rarity,
                        },
                    ],
                "inventory": "HARDCODED_VALUE",
            }
        }
    ), 200
