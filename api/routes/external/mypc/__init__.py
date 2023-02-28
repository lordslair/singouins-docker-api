# -*- coding: utf8 -*-

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.metas                import metaRaces
from nosql.models.RedisCosmetic import RedisCosmetic
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisUser     import RedisUser
from nosql.models.RedisWallet   import RedisWallet

from utils.routehelper          import (
    creature_check,
    )


#
# Routes /mypc/*
#
# API: POST /mypc
@jwt_required()
def mypc_add():
    User = RedisUser(get_jwt_identity())
    h = f'[User.id:{User.id}]'

    pcclass      = request.json.get('class', None)
    pccosmetic   = request.json.get('cosmetic', None)
    pcequipment  = request.json.get('equipment', None)
    pcgender     = request.json.get('gender', None)
    pcname       = request.json.get('name', None)
    pcrace       = request.json.get('race', None)

    if len(RedisSearch().creature(query=f'@name:{pcname}').results) != 0:
        msg = f'{h} Creature already exists (Creature.name:{pcname})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # We grab the race wanted from metaRaces
        metaRace = dict(list(filter(lambda x: x["id"] == pcrace,
                                    metaRaces))[0])  # Gruikfix
        if metaRace is None:
            msg = f'{h} MetaRace not found (race:{pcrace})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        try:
            Creature = RedisCreature().new(
                name=pcname,
                raceid=pcrace,
                gender=pcgender,
                accountuuid=User.id,
                )
        except Exception as e:
            msg = f'{h} PC creation KO (pcname:{pcname}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            if Creature is None:
                msg = f'{h} PC creation KO (pcname:{pcname})'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                h = f'[Creature.id:{Creature.id}]'  # Header for logging

            try:
                # We initialize a fresh wallet
                Wallet = RedisWallet(creatureuuid=Creature.id).new()
            except Exception as e:
                msg = f'{h} Wallet creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                if Wallet:
                    logger.trace(f'{h} Wallet creation OK')
                else:
                    logger.warning(f'{h} Wallet creation KO')

            try:
                RedisCosmetic().new(
                    creatureuuid=Creature.id,
                    cosmetic_caracs=pccosmetic,
                    )
            except Exception as e:
                msg = f'{h} Cosmetics creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                logger.trace(f'{h} Cosmetics creation OK')

            try:
                HighScores = RedisHS(creatureuuid=Creature.id)
                HighScores.incr('global_kills')
                HighScores.incr('global_deaths')
            except Exception as e:
                msg = f'{h} RedisHS creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                logger.trace(f'{h} RedisHS creation OK')

            try:
                RedisSlots().new(creatureuuid=Creature.id)
            except Exception as e:
                msg = f'{h} RedisSlots creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                logger.trace(f'{h} RedisSlots creation OK')

            if pcequipment:
                try:
                    # Items are added
                    if pcequipment['righthand'] is not None:
                        RedisItem().new(
                            creatureuuid=Creature.id,
                            item_caracs={
                                "metatype":
                                    pcequipment['righthand']['metatype'],
                                "metaid":
                                    pcequipment['righthand']['metaid'],
                                "bound": True,
                                "bound_type": 'BoP',
                                "modded": False,
                                "mods": None,
                                "state": 100,
                                "rarity": 'Common'
                                }
                            )

                    if pcequipment['lefthand'] is not None:
                        RedisItem().new(
                            creatureuuid=Creature.id,
                            item_caracs={
                                "metatype":
                                    pcequipment['lefthand']['metatype'],
                                "metaid":
                                    pcequipment['lefthand']['metaid'],
                                "bound": True,
                                "bound_type": 'BoP',
                                "modded": False,
                                "mods": None,
                                "state": 100,
                                "rarity": 'Common'
                                }
                            )
                except Exception as e:
                    msg = f'{h} Weapons creation KO [{e}]'
                    logger.error(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
                else:
                    # Everything has been populated. Stats can be done
                    msg = f'{h} Weapons creation OK'
                    logger.trace(msg)
                    try:
                        # We initialize a fresh stats
                        RedisStats().new(Creature=Creature, classid=pcclass)
                    except Exception as e:
                        msg = f'{h} RedisStats creation KO [{e}]'
                        logger.error(msg)
                        return jsonify(
                            {
                                "success": False,
                                "msg": msg,
                                "payload": None,
                            }
                        ), 200
                    else:
                        logger.trace(f'{h} RedisStats creation OK')

            # Everything went well
            msg = f'{h} Creature creation OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Creature.as_dict(),
                }
            ), 201


# API: GET /mypc
@jwt_required()
def mypc_get_all():
    User = RedisUser(username=get_jwt_identity())
    h = f'[User.id:{User.id}]'

    try:
        Creatures = RedisSearch().creature(
            query=f"@account:{User.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = (
            f'{h} Creatures query KO '
            f'(username:{get_jwt_identity()}) [{e}]'
            )
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Creatures Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [
                    Creature.as_dict() for Creature in Creatures.results
                    ],
            }
        ), 200


# API: DELETE /mypc/<uuid:creatureuuid>
@jwt_required()
def mypc_del(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature)

    if Creature.instance:
        msg = f'{h} Creature should not be in an Instance({Creature.instance})'
        logger.debug(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        # We start do delete PC elements
        if RedisStats(creatureuuid=Creature.id).destroy():
            logger.trace(f'{h} RedisStats delete OK')
        if RedisWallet(creatureuuid=Creature.id).destroy():
            logger.trace(f'{h} Wallet delete OK')
        if RedisSlots(creatureuuid=Creature.id).destroy():
            logger.trace(f'{h} RedisSlots delete OK')
        if RedisHS(creatureuuid=Creature.id).destroy():
            logger.trace(f'{h} RedisHS delete OK')
        if RedisPa(creatureuuid=Creature.id).destroy():
            logger.trace(f'{h} RedisPa delete OK')

        # We delete all the items belonging to the Creature
        try:
            # Finding all Creature items to loop on
            Items = RedisSearch().item(
                query=f"@bearer:{Creature.id.replace('-', ' ')}",
                )
            Cosmetics = RedisSearch().cosmetic(
                query=f"@bearer:{Creature.id.replace('-', ' ')}",
                )
        except Exception as e:
            logger.error(f'{h} Items Query KO [{e}]')
        else:
            if Items and len(Items.results) > 0:
                try:
                    for Item in Items.results:
                        RedisItem(itemuuid=Item.id).destroy()
                except Exception as e:
                    logger.error(f'{h} RedisItem(s) delete KO [{e}]')
                else:
                    logger.trace(f'{h} RedisItem(s) delete OK')
            if Cosmetics and len(Cosmetics.results) > 0:
                try:
                    for Cosmetic in Cosmetics.results:
                        RedisCosmetic(cosmeticuuid=Cosmetic.id).destroy()
                except Exception as e:
                    logger.error(f'{h} RedisCosmetic(s) delete KO [{e}]')
                else:
                    logger.trace(f'{h} RedisCosmetic(s) delete OK')

        # Now we can delete the Creature itself
        Creature.destroy()
    except Exception as e:
        msg = f'{h} Creature delete KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Creature delete OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
