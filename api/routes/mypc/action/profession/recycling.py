# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Highscore import HighscoreDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from routes.mypc.action.profession._tools import (
    probabilistic_binary,
    profession_gain,
    profession_scaled,
    )
from utils.redis import get_pa
from variables import rarity_array

#
# Profession.recycling specifics
#
PA_COST_RED = 0
PA_COST_BLUE = 2
PROFESSION_NAME = 'recycling'


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST /mypc/<uuid:creatureuuid>/action/profession/recycling/<uuid:itemuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
@check_creature_pa(red=PA_COST_RED, blue=PA_COST_BLUE)
def recycling(creatureuuid, itemuuid):
    Profession = ProfessionDocument.objects(_id=creatureuuid).get()

    varx = 5 - rarity_array['item'].index(g.Item.rarity)   # between 0 and 5
    vary = profession_scaled(Profession.recycling)         # between 0 and 4
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

    # We update the Profession score
    profession_gain(g.Creature.id, PROFESSION_NAME, Profession.recycling)

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
