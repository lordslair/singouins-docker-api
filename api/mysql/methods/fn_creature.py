# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *
from ..utils.loot       import *
from .fn_globals        import clog

def fn_creature_tag(pc,tg):
    session = Session()
    try:
        tg.targeted_by = pc.id
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Targeted_by update failed (pcid:{},tgid:{})'.format(pc.id,tg.id),
                None)
    else:
        clog(tg.id,None,'Targeted by {}'.format(pc.name))
    finally:
        session.close()

def fn_creature_wound(pc,tg,hp):
    session = Session()
    try:
        tg    = session.query(PJ).filter(PJ.id == targetid).one_or_none()
        tg.hp = tg.hp - dmg
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200, False, 'HP update failed', None)
    else:
        clog(tg.id,None,'Suffered minor injuries')
    finally:
        session.close()

def fn_creature_kill(pc,tg):
    clog(pc.id,tg.id,'Killed {}'.format(tg.name))
    clog(tg.id,None,'Died'.format(pc.name))

def fn_creature_gain_xp(pc,tg):
    session = Session()
    try:
        if pc.squad is None:
            # We add PX only to the killer
            pc.xp  += tg.level       # We add XP
            pc.date = datetime.now() # We update date
        else:
            # We add PX to the killer squad
            squadlist = session.query(PJ)\
                               .filter(PJ.squad == pc.squad)\
                               .filter(PJ.squad_rank != 'Pending').all()
            for pcsquad in squadlist:
                pcsquad.xp  += round(tg.level/len(squadlist)) # We add XP
                pcsquad.date = datetime.now()                 # We update date
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (False,
                '[SQL] XP update failed (pcid:{},tgid:{})'.format(pc.id,tg.id))
    else:
        clog(pc.id,None,'Gained Experience')
        return (True, None)
    finally:
        session.close()

def fn_creature_gain_loot(pc,tg):
    session = Session()
    try:
        if pc.squad is None:
            # Loots are generated
            loots   = get_loots(tg)
            # We add loot only to the killer
            equipment         = session.query(CreaturesSlots)\
                                       .filter(CreaturesSlots.id == pc.id)\
                                       .one_or_none()
            equipment.wallet += loots[0]['currency'] # We add currency
            equipment.date    = datetime.now()   # We update the date in DB
        else:
            # We add loot to the killer squad
            squadlist = session.query(PJ)\
                               .filter(PJ.squad == pc.squad)\
                               .filter(PJ.squad_rank != 'Pending').all()
            for pcsquad in squadlist:
                # Loots are generated
                loots   = get_loots(tg)
                equipment         = session.query(CreaturesSlots)\
                                           .filter(CreaturesSlots.id == pcsquad.id)\
                                           .one_or_none()
                equipment.wallet += round(loots[0]['currency']/len(squadlist)) # We add currency
                equipment.date    = datetime.now()                             # We update the date in DB

                if loots[0]['item'] is not None:
                    # Items are added
                    item = Items(metatype   = loots[0]['item']['metatype'],
                                 metaid     = loots[0]['item']['metaid'],
                                 bearer     = pcsquad.id,
                                 bound      = loots[0]['item']['bound'],
                                 bound_type = loots[0]['item']['bound_type'],
                                 modded     = False,
                                 mods       = None,
                                 state      = randint(0,100),
                                 rarity     = loots[0]['item']['rarity'],
                                 offsetx    = None,
                                 offsety    = None,
                                 date       = datetime.now())
                    session.add(item)
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (False,
                '[SQL] Loot update failed (pcid:{})'.format(pc.id))
    else:
        clog(pc.id,None,'Gained Loot')
        return (True, None)
    finally:
        session.close()
