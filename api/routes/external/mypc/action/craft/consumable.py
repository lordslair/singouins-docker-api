# -*- coding: utf8 -*-

from flask                      import g, jsonify, request
from flask_jwt_extended         import jwt_required
from loguru                     import logger
from random                     import choices

from nosql.metas                import (
    metaRecipes,
    metaConsumables,
    )
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisWallet   import RedisWallet

from utils.decorators import (
    check_creature_exists,
    check_is_json,
    )


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: PUT /mypc/<uuid:creatureuuid>/action/craft/consumable/<int:recipeid>
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
def consumable(creatureuuid, recipeid):
    # Retrieving recipe
    try:
        # We grab the race wanted from metaRaces
        metaRecipe = dict(
            list(
                filter(lambda x: x["id"] == recipeid, metaRecipes)
                )[0]
            )  # Gruikfix
    except Exception as e:
        msg = f'{g.h} metaRecipe Query KO (recipeid:{recipeid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if metaRecipe is None:
        msg = f'{g.h} metaRecipe NotFound (recipeid:{recipeid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We load a lot of Redis Objects for later
    Wallet = RedisWallet(creatureuuid=g.Creature.id)
    HighScores = RedisHS(creatureuuid=g.Creature.id)

    # Check if requirements are met WITH extra components
    request_data = request.get_json()
    if 'extra' in request_data:
        wallet_needed = request_data['extra']
        # We iterate over what we need
        for key, needed_value in wallet_needed.items():
            # We compare with what is possessed
            if needed_value > 0:
                wallet_value = getattr(Wallet, key)
                if wallet_value >= needed_value:
                    setattr(Wallet, key, wallet_value - needed_value)
                else:
                    msg = f'{g.h} Not enough. Wallet.{key} < ({needed_value})'
                    logger.warning(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
        # We are on the recipe with extra component
        # Lets find the % of success
        if request_data['extra']['legendary'] > 0:
            success_percent_t2 = 55
            success_percent_t1 = 45
            success_percent_t0 = 0
        elif request_data['extra']['epic'] > 0:
            success_percent_t2 = 40
            success_percent_t1 = 60
            success_percent_t0 = 0
        elif request_data['extra']['rare'] > 0:
            success_percent_t2 = 25
            success_percent_t1 = 60
            success_percent_t0 = 15
        elif request_data['extra']['uncommon'] > 0:
            success_percent_t2 = 10
            success_percent_t1 = 60
            success_percent_t0 = 30
        elif request_data['extra']['common'] > 0:
            success_percent_t2 = 10
            success_percent_t1 = 45
            success_percent_t0 = 45
        else:
            # Something maybe was fucked up, we apply base %
            success_percent_t2 = 10
            success_percent_t1 = 30
            success_percent_t0 = 60

        # Now we check if we need to remoce currency from wallet
        if 'currency' in metaRecipe['component']['wallet']:
            # OK, we have to
            currency = metaRecipe['component']['wallet']['currency']
            if g.Creature.race in [1, 2, 3, 4]:
                # Creature is a Singouin, we remove bananas
                Wallet.bananas -= currency
            elif g.Creature.race in [5, 6, 7, 8]:
                # Creature is a Pourchon, we remove sausages
                Wallet.sausages -= currency
            else:
                # We fucked up
                pass
    else:
        msg = f'{g.h} Not enough data'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We are on the original recipe, no extra component
    # Lets set the % of success
    success_percent_t2 = 10
    success_percent_t1 = 30
    success_percent_t0 = 60

    crafted_tier = choices(
        [2, 1, 0],
        weights=(
            success_percent_t2 + int(HighScores.craft_potion / 5),
            success_percent_t1 + int(HighScores.craft_potion / 5),
            success_percent_t0 + int(HighScores.craft_potion / 5),
            ),
        k=1)[0]

    # We find the crafted item with the related tier
    # As we can create only Potions with this route ...
    metaConsumable = dict(
        list(
            filter(
                lambda x: (
                    x["name"] == metaRecipe['name']
                    and x["tier"] == crafted_tier
                    ),
                metaConsumables
                )
            )[0]
        )  # Gruikfix
    logger.debug(f'{g.h} Crafted item:{metaConsumable}')

    # We set the HS
    HighScores.incr(metaRecipe['hs'])

    # We create the Creature Event
    RedisEvent().new(
        action_src=g.Creature.id,
        action_dst=None,
        action_type='action/craft',
        action_text='Crafted something',
        action_ttl=30 * 86400
        )

    # TODO:
    """
    Here we should add the REAL creation of the consumable
    IE: Add it into the inventory
    But that will be for later, here is just a prototype
    """

    msg = f'{g.h} Craft Query OK (recipeid:{recipeid})'
    logger.debug(msg)

    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": metaConsumable,
        }
    ), 200
