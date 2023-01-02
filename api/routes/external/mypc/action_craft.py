# -*- coding: utf8 -*-

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger
from random                     import choices

from nosql.metas                import (
    metaRecipes,
    metaConsumables,
    )
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisWallet   import RedisWallet
from nosql.models.RedisUser     import RedisUser

from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

#
# Routes /mypc/{pcid}/action
#


# API: PUT /mypc/{pcid}/action/craft/consumable/{recipeid}
@jwt_required()
def action_craft_consumable(pcid, recipeid):
    request_json_check(request)
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    # Retrieving recipe
    try:
        # We grab the race wanted from metaRaces
        metaRecipe = dict(
            list(
                filter(lambda x: x["id"] == recipeid, metaRecipes)
                )[0]
            )  # Gruikfix
    except Exception as e:
        msg = f'{h} metaRecipe Query KO (recipeid:{recipeid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if metaRecipe is None:
        msg = f'{h} metaRecipe NotFound (recipeid:{recipeid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We load a lot of Redis Objects for later
    Wallet = RedisWallet(Creature)
    HighScores = RedisHS(Creature)

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
                    msg = f'{h} Not enough. Wallet.{key} < ({needed_value})'
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
            if Creature.race in [1, 2, 3, 4]:
                # Creature is a Singouin, we remove bananas
                Wallet.bananas -= currency
            elif Creature.race in [5, 6, 7, 8]:
                # Creature is a Pourchon, we remove sausages
                Wallet.sausages -= currency
            else:
                # We fucked up
                pass
    else:
        msg = f'{h} Not enough data'
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
    logger.debug(f'{h} Crafted item:{metaConsumable}')

    # We set the HS
    HighScores.incr(metaRecipe['hs'])

    # We create the Creature Event
    RedisEvent(Creature).add(
        Creature.id,
        None,
        'action/craft',
        'Crafted something',
        30 * 86400
        )

    # TODO:
    """
    Here we should add the REAL creation of the consumable
    IE: Add it into the inventory
    But that will be for later, here is just a prototype
    """

    msg = f'{h} Craft Query OK (recipeid:{recipeid})'
    logger.debug(msg)

    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": metaConsumable,
        }
    ), 200
