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

def mypc_create(username,pcname,pcrace,pcclass,base_equipment):
    session = Session()

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
