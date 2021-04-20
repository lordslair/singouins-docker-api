# -*- coding: utf8 -*-

import                  json

from datetime           import datetime
from random             import randint

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /mypc/*
#

# API: POST /mypc
def mypc_create(username,pcname,pcrace,pcclass,pcequipment,pccosmetic):
    session = Session()

    mypc_nbr = mypc_get_all(username)[3]
    if mypc_nbr:
        if len(mypc_nbr) >= 3:
            return (200,
                    False,
                    f'PC quota reached (username:{username},pccount:{len(mypc_nbr)})',
                    None)

    if fn_creature_get(pcname,None)[1]:
        return (409,
                False,
                f'PC already exists (username:{username},pcname:{pcname})',
                None)
    else:
        race = session.query(MetaRace).filter(MetaRace.id == pcrace).one_or_none()
        if race is None:
            return (200,
                    False,
                    f'MetaRace not found (race:{pcrace})',
                    None)

        pc = PJ(name    = pcname,
                race    = race.id,
                account = fn_user_get(username).id,
                hp      = 100 + race.min_m,
                hp_max  = 100 + race.min_m,
                x       = randint(2,4), # TODO: replace with rand(empty coords)
                y       = randint(2,5)) # TODO: replace with rand(empty coords)

        session.add(pc)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (200,
                    False,
                    f'[SQL] PC creation failed (username:{username},pcname:{pcname}) [{e}]',
                    None)
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
                                          m_race = race.min_m,
                                          r_race = race.min_r,
                                          g_race = race.min_g,
                                          v_race = race.min_v,
                                          p_race = race.min_p,
                                          b_race = race.min_b)

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
                    # Something went wrong during commit
                    session.rollback()
                    return (200,
                            False,
                            f'[SQL] PC Slots/Wallet/HS/Stats creation failed [{e}]',
                            None)
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
                                 itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == rh.metaid).one_or_none()
                                 # item.ammo is by default None, we initialize it here
                                 if itemmeta.ranged == True:
                                     rh.ammo = itemmeta.max_ammo

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
                                 itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == lh.metaid).one_or_none()
                                 # item.ammo is by default None, we initialize it here
                                 if itemmeta.ranged == True:
                                     lh.ammo = itemmeta.max_ammo

                    try:
                        session.commit()
                    except Exception as e:
                        # Something went wrong during commit
                        session.rollback()
                        return (200,
                                False,
                                f'[SQL] PC Wallet/Inventory population failed [{e}]',
                                None)
                    else:
                        return (201,
                                True,
                                f'PC successfully created (pcid:{pc.id})',
                                pc)
        finally:
            session.close()

# API: GET /mypc
def mypc_get_all(username):
    session = Session()

    try:
        userid = fn_user_get(username).id
        pcs    = session.query(PJ).filter(PJ.account == userid).all()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[SQL] PCs query failed (username:{username}) [{e}]',
                None)
    else:
        if pcs:
            return (200,
                    True,
                    f'PCs successfully found (username:{username})',
                    pcs)
        else:
            return (200,
                    False,
                    f'No PC found for this user (username:{username})',
                    None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>
def mypc_get_one(username,pcid):
    session = Session()

    try:
        userid = fn_user_get(username).id
        pcs    = session.query(PJ)\
                        .filter(PJ.account == userid, PJ.id == pcid)\
                        .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[SQL] PC query failed (username:{username},pcid:{pcid}) [{e}]',
                None)
    else:
        if pcs:
            return (200,
                    True,
                    f'PCs successfully found (username:{username},pcid:{pcid})',
                    pcs)
        else:
            return (200,
                    False,
                    f'No PC found for this user (username:{username},pcid:{pcid})',
                    None)
    finally:
        session.close()


# API: DELETE /mypc/<int:pcid>
def mypc_del(username,pcid):
    session = Session()

    if not fn_creature_get(None,pcid)[3]:
        return (200,
                False,
                f'PC does not exist (pcid:{pcid})',
                None)

    try:
        userid    = fn_user_get(username).id

        pc        = session.query(PJ).filter(PJ.account == userid, PJ.id == pcid).one_or_none()
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
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] PC deletion failed (username:{username},pcid:{pcid}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'PC successfully deleted (username:{username},pcid:{pcid})',
                None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/stats
def mypc_get_stats(pc):

    # We check if we have the data in redis
    stats = get_stats(pc)
    if stats:
        # Data was in Redis, so we return it
        return (200,
                True,
                f'Stats successfully found in Redis (pcid:{pc.id})',
                stats)

    # Data was not in Redis, so we compute it
    session      = Session()
    stats_items  = {"off":{
                            "capcom": 0,
                            "capsho": 0},
                    "def":{
                            "armor": {
                                        "p": 0,
                                        "b": 0},
                            "hpmax": 0,
                            "dodge": 0,
                            "parry": 0}}

    try:
        equipment = session.query(CreatureSlots)\
                           .filter(CreatureSlots.id == pc.id)\
                           .one_or_none()

        # Equipement Slots are items.id, not meta.id - need to double query it
        if equipment:
            feet      = session.query(Item).filter(Item.id == equipment.feet).one_or_none()
            hands     = session.query(Item).filter(Item.id == equipment.hands).one_or_none()
            head      = session.query(Item).filter(Item.id == equipment.head).one_or_none()
            shoulders = session.query(Item).filter(Item.id == equipment.shoulders).one_or_none()
            torso     = session.query(Item).filter(Item.id == equipment.torso).one_or_none()
            legs      = session.query(Item).filter(Item.id == equipment.legs).one_or_none()

            armormetas = []
            if feet:
                feetmeta      = session.query(MetaArmor).filter(MetaArmor.id == feet.metaid).one_or_none()
                armormetas.append(feetmeta)
            if hands:
                handsmeta     = session.query(MetaArmor).filter(MetaArmor.id == hands.metaid).one_or_none()
                armormetas.append(handsmeta)
            if head:
                headmeta      = session.query(MetaArmor).filter(MetaArmor.id == head.metaid).one_or_none()
                armormetas.append(headmeta)
            if shoulders:
                shouldersmeta = session.query(MetaArmor).filter(MetaArmor.id == shoulders.metaid).one_or_none()
                armormetas.append(shouldersmeta)
            if torso:
                torsometa     = session.query(MetaArmor).filter(MetaArmor.id == torso.metaid).one_or_none()
                armormetas.append(torsometa)
            if legs:
                legsmeta      = session.query(MetaArmor).filter(MetaArmor.id == legs.metaid).one_or_none()
                armormetas.append(legsmeta)

            holster   = session.query(MetaWeapon).filter(MetaWeapon.id == equipment.holster).one_or_none()
            lefthand  = session.query(MetaWeapon).filter(MetaWeapon.id == equipment.lefthand).one_or_none()
            righthand = session.query(MetaWeapon).filter(MetaWeapon.id == equipment.righthand).one_or_none()

        # We need to query Creature base stats
        cs        = session.query(CreatureStats)\
                           .filter(CreatureStats.id == pc.id)\
                           .one_or_none()

    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[SQL] CreatureSlots or CreatureStats query failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        for meta in armormetas:
            if meta:
                stats_items['def']['armor']['b'] += meta.arm_b
                stats_items['def']['armor']['p'] += meta.arm_p

        if cs:
            # We got Creature base stats
            base_m = cs.m_race + cs.m_class + cs.m_skill + cs.m_point
            base_r = cs.r_race + cs.r_class + cs.r_skill + cs.r_point
            base_g = cs.g_race + cs.g_class + cs.g_skill + cs.g_point
            base_v = cs.v_race + cs.v_class + cs.v_skill + cs.v_point
            base_p = cs.p_race + cs.p_class + cs.p_skill + cs.p_point
            base_b = cs.b_race + cs.b_class + cs.b_skill + cs.b_point
        else:
            # Something is probably wrong
            base_m = 0
            base_r = 0
            base_g = 0
            base_v = 0
            base_p = 0
            base_b = 0

        # We push data in final dict
        stats  = {"base":{
                            "m": 0 + base_m,
                            "r": 0 + base_r,
                            "g": 0 + base_g,
                            "v": 0 + base_v,
                            "p": 0 + base_p,
                            "b": 0 + base_b},
                  "off":{
                            "capcom": round((pc.g + round((base_m + base_r)/2))/2),
                            "capsho": round((pc.v + round((base_b + base_r)/2))/2)},
                  "def":{
                            "armor": {
                                        "p": 0 + stats_items['def']['armor']['p'],
                                        "b": 0 + stats_items['def']['armor']['b']},
                            "hpmax": 100 + base_m + round(pc.level/2),
                            "dodge": base_r,
                            "parry": round(((base_g-100)/50) * ((base_m-100)/50))}}

        # Data was not in Redis, so we push it
        set_stats(pc,stats)

        # To avoid errors, we return the freshly computed value
        return (200,
                True,
                f'Stats successfully computed (pcid:{pc.id})',
                stats)
    finally:
        session.close()
