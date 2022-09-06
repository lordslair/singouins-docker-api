# -*- coding: utf8 -*-

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import (fn_creature_add,
                                        fn_creature_del,
                                        fn_creature_get,
                                        fn_creature_get_all,
                                        fn_creature_stats_add,
                                        fn_creature_stats_del)
from mysql.methods.fn_inventory import (fn_cosmetic_add,
                                        fn_cosmetic_del,
                                        fn_item_add,
                                        fn_slots_add,
                                        fn_slots_del)
from mysql.methods.fn_user      import fn_user_get

from nosql.metas                import get_meta
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet

# Loading the Meta for later use
try:
    metaRaces   = get_meta('race')
    metaWeapons = get_meta('weapon')
except Exception as e:
    logger.error(f'Meta fectching KO [{e}]')
else:
    logger.trace('Meta fectching OK')


#
# Routes /mypc/*
#
# API: POST /mypc
@jwt_required()
def mypc_add():
    username = get_jwt_identity()

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

    if fn_creature_get(pcname, None)[1]:
        msg = f'PC already exists (username:{username},pcname:{pcname})'
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
            msg = f'MetaRace not found (race:{pcrace})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        try:
            pc = fn_creature_add(pcname,
                                 pcrace,
                                 pcgender,
                                 fn_user_get(username).id)
        except Exception as e:
            msg = f'PC creation KO (username:{username},pcname:{pcname}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            if pc is None:
                msg = f'PC creation KO (username:{username},pcname:{pcname})'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                h = f'[Creature.id:{pc.id}]'  # Header for logging

            try:
                # We initialize a fresh wallet
                creature_wallet = RedisWallet(pc)
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
                if fn_cosmetic_add(pc, pccosmetic):
                    logger.trace(f'{h} Cosmetic creation OK')
                else:
                    logger.warning(f'{h} Cosmetic creation KO')
                if fn_slots_add(pc):
                    logger.trace(f'{h} Slots creation OK')
                else:
                    logger.warning(f'{h} Slots creation KO')
                if fn_creature_stats_add(pc, metaRace, pcclass):
                    logger.trace(f'{h} Stats creation OK (MySQL)')
                else:
                    logger.warning(f'{h} Stats creation KO (MySQL)')
            except Exception as e:
                msg = f'{h} PC Cosmetics/Slots/Stats creation KO [{e}]'
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
                            fn_item_add(pc, rh_caracs)

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
                            fn_item_add(pc, lh_caracs)

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
                            redis_stats = RedisStats(pc)
                            # We immediately store it
                            redis_stats.store()
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
                        "payload": pc,
                    }
                ), 201


# API: GET /mypc
@jwt_required()
def mypc_get_all():
    username = get_jwt_identity()

    try:
        userid = fn_user_get(username).id
        pcs    = fn_creature_get_all(userid)
    except Exception as e:
        msg = f'[SQL] PCs query KO (username:{username}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if pcs:
            msg = f'PCs Query OK (username:{username})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": pcs,
                }
            ), 200
        else:
            msg = f'No PC found for this user (username:{username})'
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
    creature = fn_creature_get(None, pcid)[3]

    if creature is None:
        msg = f'Creature({pcid}) does not exist'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging

    if creature.instance:
        msg = f'{h} Creature should not be in an Instance({creature.instance})'
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
        if fn_cosmetic_del(creature):
            logger.trace(f'{h} Cosmetics delete OK')
        if fn_slots_del(creature):
            logger.trace(f'{h} Slots delete OK')

        if fn_creature_stats_del(creature):
            logger.trace(f'{h} Stats delete OK (MySQL)')
        if RedisStats(creature).destroy():
            logger.trace(f'{h} Stats delete OK (Redis)')

        if RedisWallet(creature).destroy():
            logger.trace(f'{h} RedisWallet delete OK')

        if RedisHS(creature).destroy():
            logger.trace(f'{h} RedisHS delete OK')

        """
        # We leave the instance if we are in one
        if creature.instance:
            if len(fn_creatures_in_instance(creature.instance)) == 1:
                # The creature is the last in Instance, we destroy it quickly
                if RedisInstance(creature).destroy():
                    logger.trace(f'{h} Instance leave OK')
                else:
                    logger.trace(f'{h} Instance leave KO')
                    """

        # Now we can delete tue PC itself
        if fn_creature_del(creature):
            logger.trace(f'{h} Creature delete OK (MySQL)')
        else:
            logger.warning(f'{h} Creature delete KO (MySQL)')

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
