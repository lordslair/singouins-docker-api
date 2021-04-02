# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import PJ,Wallet,Item
from ..utils.loot       import *
from ..utils.redis      import *

from .fn_global         import clog

def fn_creature_get(pcname,pcid):
    session = Session()

    try:
        if pcid:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
        elif pcname:
            pc = session.query(PJ).filter(PJ.name == pcname).one_or_none()
        else:
            return (200,
                    False,
                    'Wrong pcid/pcname (pcid:{},pcname:{})'.format(pcid,pcname),
                    None)
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] PC query failed (pcid:{},pcname:{})'.format(pcid,pcname),
                None)
    else:
        if pc:
            return (200,
                    True,
                    'PC successfully found (pcid:{},pcname:{})'.format(pcid,pcname),
                    pc)
        else:
            return (200,
                    False,
                    'PC does not exist (pcid:{},pcname:{})'.format(pcid,pcname),
                    None)
    finally:
        session.close()

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

def fn_creature_wound(pc,tg,dmg):
    session = Session()
    try:
        tg      = session.query(PJ).filter(PJ.id == tg.id).one_or_none()
        tg.hp   = tg.hp - dmg    # We update Health Points
        tg.date = datetime.now() # We update date
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200, False, 'HP update failed', None)
    else:
        clog(tg.id,None,'Suffered minor injuries')
    finally:
        session.close()

def fn_creature_kill(pc,tg):
    session = Session()

    # As tg object will be destroyed, we store the info for later
    tgid    = tg.id
    tgname  = tg.name

    try:
        tg      = session.query(PJ).filter(PJ.id == tg.id).one_or_none()
        tg.hp   = 0              # We update Health Points
        tg.date = datetime.now() # We update date
        #session.delete(tg)
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] PC Kill failed (tgid:{},tgname:{})'.format(tgid,tgname),
                None)
    else:
        # We put the info in queue for ws
        qciphered = False
        qpayload  = {"id": pc.id, "target": {"id": tgid, "name": tgname}}
        qscope    = {"id": None, "scope": 'broadcast'}
        qmsg = {"ciphered": qciphered,
                "payload": qpayload,
                "route": "mypc/{id1}/action/attack/{id2}/{id3}",
                "scope": qscope}
        yqueue_put('broadcast', qmsg)

        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": f':pirate_flag: **[{pc.id}] {pc.name}** killed **[{tgid}] {tgname}**',
                "route": None,
                "scope": f'Squad-{pc.squad}'}
        yqueue_put('discord', qmsg)

        clog(pc.id,tgid,f'Killed {tgname}')
        clog(tgid,None,'Died')
        return (200,
                True,
                '[SQL] PC Kill successed (tgid:{},tgname:{})'.format(tgid,tgname),
                None)
    finally:
        session.close()

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
            wallet           = session.query(Wallet)\
                                      .filter(Wallet.id == pc.id)\
                                      .one_or_none()
            currency         = loots[0]['currency']
            wallet.currency += currency       # We add currency
            wallet.date      = datetime.now() # We update the date in DB

            incr_hs(pc,f'combat:loot:currency', currency) # Redis HighScore
        else:
            # We add loot to the killer squad
            squadlist = session.query(PJ)\
                               .filter(PJ.squad == pc.squad)\
                               .filter(PJ.squad_rank != 'Pending').all()
            for pcsquad in squadlist:
                # Loots are generated
                loots            = get_loots(tg)
                wallet           = session.query(Wallet)\
                                          .filter(Wallet.id == pcsquad.id)\
                                          .one_or_none()
                currency = round(loots[0]['currency']/len(squadlist))
                wallet.currency += currency       # We add currency
                wallet.date      = datetime.now() # We update the date in DB

                incr_hs(pcsquad,f'combat:loot:currency', currency) # Redis HighScore

                if loots[0]['item'] is not None:
                    # Items are added
                    item = Item(metatype   = loots[0]['item']['metatype'],
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
                    incr_hs(pc,f'combat:loot:item:{item.rarity}', 1) # Redis HighScore
                    # We put the info in queue for ws
                    payload = f':package: **[{pcsquad.id}] {pcsquad.name}** looted something {item.rarity} !'
                    qmsg = {"ciphered": False,
                            "payload": payload,
                            "route": None,
                            "scope": f'Squad-{pc.squad}'}
                    yqueue_put('discord', qmsg)
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
