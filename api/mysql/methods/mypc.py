# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /mypc/*
#

# API: POST /mypc
def mypc_create(username,pcname,pcrace,pcclass,base_equipment):
    session = Session()

    mypc_nbr = mypc_get_all(username)[3]
    if len(mypc_nbr) >= 3:
        return (200,
                False,
                f'PC quota reached (username:{username},pccount:{len(mypc_nbr)})',
                None)

    if fn_creature_get(pcname,None)[1]:
        return (409,
                False,
                'PC already exists (username:{},pcname:{})'.format(username,pcname),
                None)
    else:
        race = session.query(MetaRace).filter(MetaRace.id == pcrace).one_or_none()
        if race is None:
            return (200,
                    False,
                    'MetaRce not found (race:{})'.format(pcrace),
                    None)

        pc = PJ(name    = pcname,
                race    = race.id,
                account = fn_user_get(username).id,
                hp      = 100 + race.min_m,
                hp_max  = 100 + race.min_m)

        session.add(pc)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (200,
                    False,
                    '[SQL] PC creation failed (username:{},pcname:{})'.format(username,pcname),
                    None)
        else:
                pc        = fn_creature_get(pcname,None)[3]
                equipment = CreatureSlots(id = pc.id)
                wallet    = Wallet(id = pc.id)
                highscore = HighScore(id = pc.id)

                stats     = CreatureStats(id = pc.id,
                                          m_race = race.min_m,
                                          r_race = race.min_r,
                                          g_race = race.min_g,
                                          v_race = race.min_v,
                                          p_race = race.min_p,
                                          b_race = race.min_b)

                session.add(equipment)
                session.add(wallet)
                session.add(highscore)
                session.add(stats)

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
                    return (200, False, '[SQL] PC Slots/Wallet/HS/Stats creation failed', None)
                else:
                    # Money is added
                    wallet.currency = 250

                    if base_equipment:
                        # Items are added
                        if base_equipment['righthand'] is not None:
                            rh   = Item(metatype   = base_equipment['righthand']['metatype'],
                                        metaid     = base_equipment['righthand']['metaid'],
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

                            if base_equipment['lefthand'] is not None:
                                lh   = Item(metatype   = base_equipment['lefthand']['metatype'],
                                        metaid     = base_equipment['lefthand']['metaid'],
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

                    try:
                        session.commit()
                    except Exception as e:
                        # Something went wrong during commit
                        return (200, False, '[SQL] PC Wallet/Inventory population failed', None)
                    else:
                        return (201, True, 'PC successfully created', pc)
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
                '[SQL] PCs query failed (username:{})'.format(username),
                None)
    else:
        if pcs:
            return (200,
                    True,
                    'PCs successfully found (username:{})'.format(username),
                    pcs)
        else:
            return (200,
                    False,
                    'No PC found for this user (username:{})'.format(username),
                    None)
    finally:
        session.close()

# API: DELETE /mypc/<int:pcid>
def mypc_del(username,pcid):
    session = Session()

    if not get_pc_exists(None,pcid):
        return (200, False, 'PC does not exist (pcid:{})'.format(pcid), None)

    try:
        userid    = fn_user_get(username).id

        pc        = session.query(PJ).filter(PJ.account == userid, PJ.id == pcid).one_or_none()
        equipment = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).one_or_none()
        wallet    = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()
        highscore = session.query(HighScore).filter(HighScore.id == pc.id).one_or_none()
        stats     = session.query(CreatureStats).filter(CreatureStats.id == pc.id).one_or_none()

        if pc: session.delete(pc)
        if equipment: session.delete(equipment)
        if wallet: session.delete(wallet)
        if highscore: session.delete(highscore)
        if stats: session.delete(stats)

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
                '[SQL] PC deletion failed (username:{},pcid:{})'.format(username,pcid),
                None)
    else:
        return (200,
                True,
                'PC successfully deleted (username:{},pcid:{})'.format(username,pcid),
                None)
    finally:
        session.close()
