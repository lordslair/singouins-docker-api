# -*- coding: utf8 -*-

import datetime
import math

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from random import choices, random

from mongo.models.Highscore import HighscoreDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    check_creature_pa,
    )
from utils.redis import get_pa, consume_pa
from variables import rarity_array

#
# Profession.recycling specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'recycling'


def profession_gain(profession_score):
    """Return the Profession score gained (0 or 1)."""
    # Define thresholds and corresponding weights
    THRESHOLDS = [
        (100, None),      # No action needed
        (75, (70, 30)),   # 75-99 → 70% 0, 30% 1
        (50, (60, 40)),   # 50-74 → 60% 0, 40% 1
        (25, (50, 50)),   # 25-49 → 50% 0, 50% 1
        (0, None)         # 0-24 → Always 1
    ]
    # Profession  → Probability to gain 1 point
    #  75 - 99    | [██████..............] 30%
    #  50 - 74    | [████████............] 40%
    #  25 - 49    | [██████████..........] 50%
    #   0 - 24    | [████████████████████] 100%

    # We calculate the amount of Profession points acquired
    for THRESHOLD, weights in THRESHOLDS:
        if profession_score >= THRESHOLD:
            if weights is None:
                return 1 if THRESHOLD == 0 else 0  # Force 1 only for the lowest threshold
            else:
                return choices([0, 1], weights=weights)[0]
            break  # Stop once we find the right range


def scaled_profession(profession_score):
    """Return the shards gained based on Profession score."""
    # Profession  → Probability to gain shards
    #  00 - 25    | [....................] 0
    #  26 - 50    | [█████...............] 1
    #  51 - 75    | [██████████..........] 2
    #  76 - 99    | [███████████████.....] 3
    #      100    | [████████████████████] 4
    return math.floor(profession_score/25)


def scaled_b(stats_b):
    """Compute the scaled value as probability."""
    return 1 - math.pow(math.exp(-(stats_b - 100) / 50), 1.5)


def probabilistic_binary(stats_b):
    """Return 1 with probability scaled_b(stats_b), else return 0."""
    # Stats.b   → Probability to gain 1 additional shard
    # 100 - 119 | [██...................] 11%
    # 120 - 139 | [████.................] 22%
    # 140 - 159 | [███████..............] 35%
    # 160 - 179 | [███████████..........] 53%
    # 180 - 199 | [██████████████.......] 69%
    # 200 - 219 | [████████████████.....] 81%
    # 220 - 239 | [██████████████████...] 89%
    # 240 - 259 | [███████████████████..] 94%
    # 260 - 279 | [████████████████████.] 97%
    # 280 - 299 | [████████████████████.] 98%
    # 300+      | [████████████████████.] 99%
    return 1 if random() < scaled_b(stats_b) else 0


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

    # We INCR the Profession accordingly
    if profession_gain(Profession.recycling) >= 1:
        profession_update_query = {
            f'inc__{PROFESSION_NAME}': profession_gain(Profession.recycling),
            "set__updated": datetime.datetime.utcnow(),
            }
        Profession.update(**profession_update_query)

    varx = 5 - rarity_array['item'].index(g.Item.rarity)   # between 0 and 5
    vary = scaled_profession(Profession.recycling)         # between 0 and 4
    varz = probabilistic_binary(g.Creature.stats.total.b)  # between 0 and 1

    # We roll the dice and calculate the total quantity
    shards_qty = varx + vary + varz
    logger.trace(f"{g.h} Roll for {PROFESSION_NAME}: {varx} + {vary} + {varz} == {shards_qty}")

    # We set the HighScores
    highscores_update_query = {
        f'inc__profession__{PROFESSION_NAME}': 1,
        'inc__internal__item__recycled': 1,
        'inc__internal__shard__obtained': shards_qty,
        "set__updated": datetime.datetime.utcnow(),
        }
    HighscoreDocument.objects(_id=g.Creature.id).update_one(**highscores_update_query)

    # We add the resources in the Satchel
    Satchel = SatchelDocument.objects(_id=creatureuuid).get()
    satchel_update_query = {
        f"inc__shard__{g.Item.rarity.lower()}": shards_qty,
        "set__updated": datetime.datetime.utcnow(),
        }
    Satchel.update(**satchel_update_query)
    Satchel.reload()

    # We consume the PA
    consume_pa(creatureuuid=creatureuuid, bluepa=PA_COST_BLUE, redpa=PA_COST_RED)

    try:
        g.Item.delete()
    except Exception as e:
        logger.error(f'{g.h} Item destroy KO (failed or no item was deleted) [{e}]')
    else:
        logger.trace(f'{g.h} Item destroy OK')

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
                        "count": shards_qty,
                        "material": 'shards',
                        "rarity": g.Item.rarity,
                        },
                    ],
                "inventory": "HARDCODED_VALUE",
                "satchel": Satchel.to_mongo(),
            }
        }
    ), 200
