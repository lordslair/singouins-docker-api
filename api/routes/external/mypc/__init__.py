# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import *
from mysql.methods.fn_inventory import *
from mysql.methods.fn_user      import *
from nosql                      import *

from nosql.models.RedisStats    import *
from nosql.models.RedisWallet   import *
from nosql.models.RedisInstance import *

# Loading the Meta for later use
try:
    metaRaces   = metas.get_meta('race')
    metaWeapons = metas.get_meta('weapon')
except Exception as e:
    logger.error(f'Meta fectching: KO [{e}]')
else:
    logger.trace(f'Meta fectching: OK')

#
# Routes /mypc/*
#
# API: POST /mypc
@jwt_required()
def mypc_add():
        username = get_jwt_identity()

        pcclass      = request.json.get('class',     None)
        pccosmetic   = request.json.get('cosmetic',  None)
        pcequipment  = request.json.get('equipment', None)
        pcgender     = request.json.get('gender',    None)
        pcname       = request.json.get('name',      None)
        pcrace       = request.json.get('race',      None)

        #mypc_nbr = mypc_get_all(username)[3]
        #if mypc_nbr:
        #    if len(mypc_nbr) >= 3:
        #        return jsonify({"success": False,
        #                        "msg": f'PC quota reached (username:{username},pccount:{len(mypc_nbr)})',
        #                        "payload": None}), 200

        if fn_creature_get(pcname,None)[1]:
            return jsonify({"success": False,
                            "msg": f'PC already exists (username:{username},pcname:{pcname})',
                            "payload": None}), 409
        else:
            # We grab the race wanted from metaRaces
            metaRace = dict(list(filter(lambda x:x["id"] == pcrace,metaRaces))[0]) # Gruikfix
            if metaRace is None:
                return jsonify({"success": False,
                                "msg": f'MetaRace not found (race:{pcrace})',
                                "payload": None}), 200
            try:
                pc = fn_creature_add(pcname,
                                     pcrace,
                                     pcgender,
                                     fn_user_get(username).id)
            except Exception as e:
                msg = f'[SQL] PC creation KO (username:{username},pcname:{pcname}) [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg": msg,
                                "payload": None}), 200
            else:
                if pc is None:
                    return jsonify({"success": False,
                                    "msg": f'PC creation KO (username:{username},pcname:{pcname}) [{e}]',
                                    "payload": None}), 200

                try:
                    # We initialize a fresh wallet
                    redis_wallet = RedisWallet(pc).init()
                except Exception as e:
                    msg = f'PC RedisWallet creation KO [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg": msg,
                                    "payload": None}), 200
                else:
                    if redis_wallet:
                        logger.trace('PC RedisWallet creation OK')
                    else:
                        logger.warning('PC RedisWallet creation KO')

                try:
                    if fn_cosmetic_add(pc,pccosmetic):
                        logger.debug('PC Cosmetic OK')
                    if fn_slots_add(pc):
                        logger.debug('PC Slots OK')
                    if fn_creature_stats_add(pc,metaRace,pcclass):
                        logger.debug('PC Stats OK')
                except Exception as e:
                    msg = f'PC Cosmetics/Slots creation KO [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg": msg,
                                    "payload": None}), 200

                else:
                    if pcequipment:
                        try:
                            # Items are added
                            if pcequipment['righthand'] is not None:
                                rh_caracs = {"metatype"  : pcequipment['righthand']['metatype'],
                                             "metaid"    : pcequipment['righthand']['metaid'],
                                             "bound"     : True,
                                             "bound_type": 'BoP',
                                             "modded"    : False,
                                             "mods"      : None,
                                             "state"     : 100,
                                             "rarity"    : 'Common'}
                                rh = fn_item_add(pc,rh_caracs)

                            if pcequipment['lefthand'] is not None:
                                lh_caracs = {"metatype"  : pcequipment['lefthand']['metatype'],
                                             "metaid"    : pcequipment['lefthand']['metaid'],
                                             "bound"     : True,
                                             "bound_type": 'BoP',
                                             "modded"    : False,
                                             "mods"      : None,
                                             "state"     : 100,
                                             "rarity"    : 'Common'}
                                lh = fn_item_add(pc,lh_caracs)

                        except Exception as e:
                            msg = f'PC Weapons creation KO [{e}]'
                            logger.error(msg)
                            return jsonify({"success": False,
                                            "msg": msg,
                                            "payload": None}), 200
                        else:
                            # Everything has been populated. Stats can be done
                            try:
                                # We initialize a fresh stats
                                redis_stats = RedisStats(pc)
                                # We immediately store it
                                redis_stats.store()
                            except Exception as e:
                                msg = f'PC RedisStats creation KO [{e}]'
                                logger.error(msg)
                                return jsonify({"success": False,
                                                "msg": msg,
                                                "payload": None}), 200
                            else:
                                logger.trace('PC RedisStats creation OK')
                                logger.debug(pc)
                                return jsonify({"success": True,
                                                "msg":     f'PC creation OK (pcid:{pc.id})',
                                                "payload": pc}), 201

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
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if pcs:
            return jsonify({"success": True,
                            "msg": f'PCs Query OK (username:{username})',
                            "payload": pcs}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'No PC found for this user (username:{username})',
                            "payload": None}), 200

# API: DELETE /mypc/<int:pcid>
@jwt_required()
def mypc_del(pcid):
    username = get_jwt_identity()
    creature = fn_creature_get(None,pcid)[3]

    if not creature:
        return jsonify({"success": False,
                        "msg": f'PC does not exist (creatureid:{creature})',
                        "payload": None}), 200

    try:
        # We start do delete PC elements
        if fn_cosmetic_del(creature):
            logger.trace('PC Cosmetics delete OK')
        if fn_slots_del(creature):
            logger.trace('PC Slots delete OK')

        if fn_creature_stats_del(creature):
            logger.trace('PC Stats delete OK (MySQL)')
        if RedisStats(creature).destroy():
            logger.trace('PC Stats delete OK (Redis)')

        if RedisWallet(creature).destroy():
            logger.trace('PC RedisWallet delete OK')

        # Now we can delete tue PC itself
        if fn_creature_del(creature):
            logger.trace('PC delete OK')

        # TODO: For now we do NOT delete items on PC deletion
    except Exception as e:
        msg = f'PC delete KO (username:{username},pcid:{pcid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'PC delete OK (username:{username},pcid:{pcid})',
                        "payload": None}), 200
