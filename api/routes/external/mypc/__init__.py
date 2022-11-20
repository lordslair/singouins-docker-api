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
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisUser     import RedisUser
from nosql.models.RedisWallet   import RedisWallet


#
# Routes /mypc/*
#
# API: POST /mypc
@jwt_required()
def mypc_add():
    username = get_jwt_identity()
    User = RedisUser().get(get_jwt_identity())
    h = f'[User.id:{User.id}]'

    pcclass      = request.json.get('class', None)
    pccosmetic   = request.json.get('cosmetic', None)
    pcequipment  = request.json.get('equipment', None)
    pcgender     = request.json.get('gender', None)
    pcname       = request.json.get('name', None)
    pcrace       = request.json.get('race', None)

    """
    mypc_nbr = mypc_get_all(username)[3]
    if mypc_nbr:
        if len(mypc_nbr) >= 3:
            msg = (f'PC quota reached '
                   f'(username:{username},pccount:{len(mypc_nbr)})')
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": pc,
                }
            ), 200
    """

    if len(RedisCreature().search(query=f'@name:{pcname}')) != 0:
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
                pcname,
                pcrace,
                pcgender,
                RedisUser().get(username).id
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
                creature_wallet = RedisWallet(Creature)
            except Exception as e:
                msg = f'{h} RedisWallet creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                if creature_wallet:
                    logger.trace(f'{h} RedisWallet creation OK')
                else:
                    logger.warning(f'{h} RedisWallet creation KO')

            try:
                if RedisCosmetic(Creature).new(pccosmetic):
                    logger.trace(f'{h} Cosmetic creation OK')
                else:
                    logger.warning(f'{h} Cosmetic creation KO')
            except Exception as e:
                msg = f'{h} PC Cosmetics creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200

            else:
                if pcequipment:
                    try:
                        # Items are added
                        if pcequipment['righthand'] is not None:
                            rh_caracs = {
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
                            RedisItem(Creature).new(rh_caracs)

                        if pcequipment['lefthand'] is not None:
                            lh_caracs = {
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
                            RedisItem(Creature).new(lh_caracs)

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
                            RedisStats(Creature).new(pcclass)
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
                        "payload": Creature._asdict(),
                    }
                ), 201


# API: GET /mypc
@jwt_required()
def mypc_get_all():
    username = get_jwt_identity()
    User = RedisUser().get(username)
    h = f'[User.id:{User.id}]'

    try:
        account = User.id.replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@account:{account}')
    except Exception as e:
        msg = f'Creatures query KO (username:{username}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Creatures:
            msg = f'{h} Creatures Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Creatures,
                }
            ), 200
        else:
            msg = f'{h} Creatures Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: DELETE /mypc/<int:pcid>
@jwt_required()
def mypc_del(pcid):
    Creature = RedisCreature().get(pcid)

    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

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
        if RedisCosmetic(Creature).destroy_all():
            logger.trace(f'{h} RedisCosmetic delete OK')
        if RedisStats(Creature).destroy():
            logger.trace(f'{h} RedisStats delete OK (Redis)')
        if RedisWallet(Creature).destroy():
            logger.trace(f'{h} RedisWallet delete OK')
        if RedisSlots(Creature).destroy():
            logger.trace(f'{h} RedisSlots delete OK')
        if RedisHS(Creature).destroy():
            logger.trace(f'{h} RedisHS delete OK')
        if RedisPa(Creature).destroy():
            logger.trace(f'{h} RedisPa delete OK')

        # Now we can delete tte Creature itself
        if RedisCreature().destroy(Creature.id):
            logger.trace(f'{h} Creature delete OK')
        else:
            logger.warning(f'{h} Creature delete KO')

        # TODO: For now we do NOT delete items on PC deletion
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
