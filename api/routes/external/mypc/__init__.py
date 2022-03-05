# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity
from random                     import randint

from mysql.methods              import fn_creature_get,fn_user_get
from mysql.models               import (Cosmetic,
                                        Creature,
                                        CreatureSlots,
                                        CreatureStats,
                                        Item,
                                        Wallet)
from mysql.session              import Session
from nosql                      import *

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
        session  = Session()
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

            pc = Creature(name    = pcname,
                          race    = metaRace['id'],
                          gender  = pcgender,
                          account = fn_user_get(username).id,
                          hp      = 100 + metaRace['min_m'], # TODO: To remove
                          hp_max  = 100 + metaRace['min_m'], # TODO: To remove
                          instance = None,        # Gruikfix for now
                          x       = randint(2,4), # TODO: replace with rand(empty coords)
                          y       = randint(2,5)) # TODO: replace with rand(empty coords)

            session.add(pc)

            try:
                session.commit()
            except Exception as e:
                session.rollback()
                msg = f'[SQL] PC creation KO (username:{username},pcname:{pcname}) [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg": msg,
                                "payload": None}), 200
            else:
                    cosmetic = Cosmetic(metaid = pccosmetic['metaid'],
                                        bearer = pc.id,
                                        bound = 1,
                                        bound_type = 'BoP',
                                        state = 99,
                                        rarity = 'Epic',
                                        data = str(pccosmetic['data']))

                    pc        = fn_creature_get(pcname,None)[3]
                    equipment = CreatureSlots(id = pc.id)
                    wallet    = Wallet(id = pc.id)

                    stats     = CreatureStats(id = pc.id,
                                              m_race = metaRace['min_m'],
                                              r_race = metaRace['min_r'],
                                              g_race = metaRace['min_g'],
                                              v_race = metaRace['min_v'],
                                              p_race = metaRace['min_p'],
                                              b_race = metaRace['min_b'])

                    session.add(equipment)
                    session.add(wallet)
                    session.add(stats)
                    session.add(cosmetic)

                    if pcclass == '1': stats.m_class = 10
                    if pcclass == '2': stats.r_class = 10
                    if pcclass == '3': stats.g_class = 10
                    if pcclass == '4': stats.v_class = 10
                    if pcclass == '5': stats.p_class = 10
                    if pcclass == '6': stats.b_class = 10

                    try:
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        msg = f'[SQL] PC Cosmetics/Slots/Wallet/Stats creation KO [{e}]'
                        logger.error(msg)
                        return jsonify({"success": False,
                                        "msg": msg,
                                        "payload": None}), 200
                    else:
                        # Money is added
                        wallet.currency = 250

                        if pcequipment:
                            # Items are added
                            if pcequipment['righthand'] is not None:
                                rh   = Item(metatype   = pcequipment['righthand']['metatype'],
                                            metaid     = pcequipment['righthand']['metaid'],
                                            bearer     = pc.id,
                                            bound      = True,
                                            bound_type = 'BoP',
                                            modded     = False,
                                            mods       = None,
                                            state      = 100,
                                            rarity     = 'Common',
                                            offsetx    = 0,
                                            offsety    = 0,
                                            date       = datetime.now())
                                session.add(rh)

                                if rh.metatype == 'weapon':
                                    # We grab the weapon wanted from metaWeapons
                                    metaWeapon = dict(list(filter(lambda x:x["id"] == rh.metaid,metaWeapons))[0]) # Gruikfix
                                    # item.ammo is by default None, we initialize it here
                                    if metaWeapon['ranged'] == True:
                                        rh.ammo = metaWeapon['max_ammo']

                            if pcequipment['lefthand'] is not None:
                                lh   = Item(metatype   = pcequipment['lefthand']['metatype'],
                                        metaid     = pcequipment['lefthand']['metaid'],
                                        bearer     = pc.id,
                                        bound      = True,
                                        bound_type = 'BoP',
                                        modded     = False,
                                        mods       = None,
                                        state      = 100,
                                        rarity     = 'Common',
                                        offsetx    = 4,
                                        offsety    = 0,
                                        date       = datetime.now())
                                session.add(lh)

                                if lh.metatype == 'weapon':
                                    # We grab the weapon wanted from metaWeapons
                                    metaWeapon = dict(list(filter(lambda x:x["id"] == lh.metaid,metaWeapons))[0]) # Gruikfix
                                    # item.ammo is by default None, we initialize it here
                                    if metaWeapon['ranged'] == True:
                                        lh.ammo = metaWeapon['max_ammo']

                        try:
                            session.commit()
                        except Exception as e:
                            session.rollback()
                            msg = f'[SQL] PC Wallet/Inventory creation KO [{e}]'
                            logger.error(msg)
                            return jsonify({"success": False,
                                            "msg": msg,
                                            "payload": None}), 200
                        else:
                            return jsonify({"success": True,
                                            "msg": f'PC creation OK (pcid:{pc.id})',
                                            "payload": pc}), 201
            finally:
                session.close()

# API: GET /mypc
@jwt_required()
def mypc_get_all():
    session  = Session()
    username = get_jwt_identity()

    try:
        userid = fn_user_get(username).id
        pcs    = session.query(Creature).filter(Creature.account == userid).all()
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
    finally:
        session.close()

# API: DELETE /mypc/<int:pcid>
@jwt_required()
def mypc_del(pcid):
    session  = Session()
    username = get_jwt_identity()

    if not fn_creature_get(None,pcid)[3]:
        return jsonify({"success": False,
                        "msg": f'PC does not exist (pcid:{pcid})',
                        "payload": None}), 200

    try:
        userid    = fn_user_get(username).id

        pc        = session.query(Creature).filter(Creature.account == userid, Creature.id == pcid).one_or_none()
        equipment = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).one_or_none()
        wallet    = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()
        stats     = session.query(CreatureStats).filter(CreatureStats.id == pc.id).one_or_none()
        cosmetics = session.query(Cosmetic).filter(Cosmetic.bearer == pc.id).one_or_none()

        if pc: session.delete(pc)
        if equipment: session.delete(equipment)
        if wallet: session.delete(wallet)
        if stats: session.delete(stats)
        if cosmetics: session.delete(cosmetics)

        items = session.query(Item).filter(Item.bearer == pc.id).all()
        if items:
            for item in items:
                # To archive the item without deleting it
                item.bearer  = None
                item.offsetx = None
                item.offsety = None

        session.commit()
    except Exception as e:
        msg = f'[SQL] PC delete KO (username:{username},pcid:{pcid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'PC delete OK (username:{username},pcid:{pcid})',
                        "payload": None}), 200
    finally:
        session.close()
