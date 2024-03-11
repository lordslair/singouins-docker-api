# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from math import floor
from random import choices, randint

from nosql.models.RedisEvent import RedisEvent
from nosql.models.RedisPa import RedisPa
from nosql.models.RedisStats import RedisStats

# TOO SOON
# from mongo.models.Highscore import HighscoreDocument

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    check_creature_pa,
    check_creature_profession,
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
@check_creature_profession(PROFESSION_NAME)
def recycling(creatureuuid, itemuuid):
    # We load a lot of Redis Objects for later
    Stats = RedisStats(creatureuuid=g.Creature.id)

    if g.Item.bearer != g.Creature.id:
        msg = f'{g.h} Item does not belong to you.'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We calculate the amount of Profession points acquired
    if 100 <= g.Profession.recycling:         # 100+
        pass
    elif 75 <= g.Profession.recycling < 100:  # 75-99
        count = choices([0, 1], weights=[70, 30])[0]
    elif 50 <= g.Profession.recycling < 75:   # 50-74
        count = choices([0, 1], weights=[60, 40])[0]
    elif 25 <= g.Profession.recycling < 50:   # 25-49
        count = choices([0, 1], weights=[50, 50])[0]
    elif g.Profession.recycling < 25:         # 0-24
        count = 1
    # We INCR the Profession accordingly
    if count >= 1:
        g.Profession.incr(PROFESSION_NAME, count=count)

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
    prof_d3 = floor(g.Profession.recycling/20)
    stat_qty = floor((Stats.p + Stats.b) / 2 / 100)

    # We roll the dice and calculate the total quantity
    shards_qty = base_qty + prof_d3 * randint(1, 3) + stat_qty
    logger.trace(f"{g.h} Roll for {PROFESSION_NAME}: {base_qty} + {prof_d3}D3 + {stat_qty}")
    logger.trace(f"{g.h} Roll for {PROFESSION_NAME}: {shards_qty}")

    # TOO SOON
    # We set the HS
    # HighScores = HighscoreDocument.objects(_id=g.Creature.id)
    # HighScores.update_one(inc__profession__recycling=1)
    # HighScores.update_one(inc__internal__item__recycled=1)
    # HighScores.update_one(inc__internal__shard__obtained=shards_qty)

    # We prepare Event message
    if shards_qty > 0:
        action_text = 'Recycled an item and got something !'
    else:
        action_text = 'Recycled an item and got nothing.'
    # We create the Creature Event
    RedisEvent().new(
        action_src=g.Creature.id,
        action_dst=None,
        action_type=f'action/profession/{PROFESSION_NAME}',
        action_text=action_text,
        action_ttl=30 * 86400
        )

    # Little snippet to check amount of resources // slots
    # slots_used = 0
    # satchel = r.json().get(f'satchels:{g.Creature.id}')
    # for resource_data in satchel['resources'].values():
    #    for resource in resource_data.values():
    #        slots_used += resource

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
