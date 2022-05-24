# -*- coding: utf8 -*-

import dataclasses

from random              import randint

from ..session           import Session
from ..models            import (Creature,
                                 CreatureSlots,
                                 CreatureStats,
                                 Item,
                                 Wallet)
from nosql               import * # Custom internal module for Redis queries

from ..utils.loot        import *

# Loading the Meta for later use
try:
    metaWeapons = metas.get_meta('weapon')
    metaRaces   = metas.get_meta('race')
except Exception as e:
    logger.error(f'Meta fectching: KO [{e}]')
else:
    logger.trace(f'Meta fectching: OK')

def fn_creature_add(name,
                    race,
                    gender,
                    accountid,
                    rarity = 'Medium',
                    x = randint(2,4),
                    y = randint(2,5),
                    instanceid = None):
    session = Session()

    try:
        # We grab the race wanted from metaRaces
        metaRace = dict(list(filter(lambda x:x["id"] == race,metaRaces))[0]) # Gruikfix
        if metaRace is None:
            logger.error(f'MetaRace not found (race:{pcrace})')
            return None

        if metaRace['id'] > 10:
            # We want to create a NPC
            name = metaRace['name']

        pc = Creature(name     = name,
                      race     = metaRace['id'],
                      rarity   = rarity,
                      gender   = gender,
                      account  = accountid,
                      hp       = 100 + metaRace['min_m'], # TODO: To remove
                      hp_max   = 100 + metaRace['min_m'], # TODO: To remove
                      instance = instanceid,
                      x        = x,
                      y        = y)

        session.add(pc)
        session.commit()
        session.refresh(pc)
    except Exception as e:
        session.rollback()
        msg = f'PC creation KO (pcname:{pcname}) [{e}]'
        logger.error(msg)
    else:
        if pc:
            return pc
        else:
            return None
    finally:
        session.close()

def fn_creature_del(creature_todel):
    session = Session()

    try:
        creature = session.query(Creature)\
                          .filter(Creature.id == creature_todel.id)\
                          .one_or_none()

        if creature: session.delete(creature)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Creature Query KO [{e}]')
        return None
    else:
        return True
    finally:
        session.close()

def fn_creature_get(pcname,pcid):
    session = Session()

    try:
        if pcid:
            pc = session.query(Creature).filter(Creature.id == pcid).one_or_none()
        elif pcname:
            pc = session.query(Creature).filter(Creature.name == pcname).one_or_none()
        else:
            message = f'Wrong pcid/pcname (pcid:{pcid},pcname:{pcname})'
            logger.warning(message)
            return (200, False, message, None)
    except Exception as e:
        message = f'[SQL] PC query failed (pcid:{pcid},pcname:{pcname}) [{e}]'
        logger.error(message)
        return (200, False, message, None)
    else:
        if pc:
            message = f'PC successfully found (pcid:{pcid},pcname:{pcname})'
            logger.trace(message)
            return (200, True, message, pc)
        else:
            message = f'PC does not exist (pcid:{pcid},pcname:{pcname})'
            logger.trace(message)
            return (200, False, message, None)
    finally:
        session.close()

def fn_creature_get_all(userid):
    session = Session()

    try:
        pcs    = session.query(Creature)\
                        .filter(Creature.account == userid)\
                        .all()
    except Exception as e:
        message = f'[SQL] PC query failed (userid:{userid}) [{e}]'
        logger.error(message)
        return None
    else:
        if pcs:
            message = f'[SQL] PC successfully found (userid:{userid})'
            logger.trace(message)
            return pcs
        else:
            return None
    finally:
        session.close()

def fn_creature_tag(pc,tg):
    session = Session()
    try:
        tg             = session.query(Creature).filter(Creature.id == tg.id).one_or_none()
        tg.targeted_by = pc.id
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Targeted_by update failed (pcid:{pc.id},tgid:{tg.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'Targeted_by update successed (pcid:{pc.id},tgid:{tg.id})',
                None)
    finally:
        session.close()

def fn_creature_kill(pc,tg,action):
    session = Session()

    # As tg object will be destroyed, we store the info for later
    tgid    = tg.id
    tgname  = tg.name

    try:
        tg      = session.query(Creature).filter(Creature.id == tg.id).one_or_none()
        session.delete(tg)
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] PC Kill failed (tgid:{tgid},tgname:{tgname}) [{e}]',
                None)
    else:
        # We put the info in queue for ws
        qciphered = False
        qpayload  = {"id": pc.id, "target": {"id": tgid, "name": tgname}, "action": action}
        qscope    = {"id": None, "scope": 'broadcast'}
        qmsg = {"ciphered": qciphered,
                "payload": qpayload,
                "route": "mypc/{id1}/action/attack/{id2}/{id3}",
                "scope": qscope}
        yqueue_put('broadcast', qmsg)

        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": f':pirate_flag: **[{pc.id}] {pc.name}** killed **[{tgid}] {tgname}**',
                "embed": None,
                "scope": f'Squad-{pc.squad}'}
        yqueue_put('yarqueue:discord', qmsg)

        return (200,
                True,
                f'PC Kill successed (tgid:{tgid},tgname:{tgname})',
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
            squadlist = session.query(Creature)\
                               .filter(Creature.squad == pc.squad)\
                               .filter(Creature.squad_rank != 'Pending').all()
            for pcsquad in squadlist:
                pcsquad.xp  += round(tg.level/len(squadlist)) # We add XP
                pcsquad.date = datetime.now()                 # We update date
        session.commit()
    except Exception as e:
        return (False,
                f'[SQL] XP update failed (pcid:{pc.id},tgid:{tg.id})')
    else:
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

            if loots[0]['item'] is not None:
                # Items are added
                item = Item(metatype   = loots[0]['item']['metatype'],
                            metaid     = loots[0]['item']['metaid'],
                            bearer     = pc.id,
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

                if   item.metatype == 'weapon':
                     itemmeta = dict(list(filter(lambda x:x["id"] == item.metaid,metaWeapons))[0]) # Gruikfix
                     # item.ammo is by default None, we initialize it here
                     if itemmeta['ranged'] == True:
                         item.ammo = 0
                elif item.metatype == 'armor':
                     itemmeta = dict(list(filter(lambda x:x["id"] == item.metaid,metaArmors))[0]) # Gruikfix
        else:
            # We add loot to the killer squad
            squadlist = session.query(Creature)\
                               .filter(Creature.squad == pc.squad)\
                               .filter(Creature.squad_rank != 'Pending').all()
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

                    if   item.metatype == 'weapon':
                        itemmeta = dict(list(filter(lambda x:x["id"] == item.metaid,metaWeapons))[0]) # Gruikfix
                        # item.ammo is by default None, we initialize it here
                        if itemmeta['ranged'] == True:
                            item.ammo = 0
                    elif item.metatype == 'armor':
                        itemmeta = dict(list(filter(lambda x:x["id"] == item.metaid,metaArmors))[0]) # Gruikfix

                    # We put the info in queue for ws Discord
                    qmsg = {"ciphered": False,
                            "payload": {"color_int": color_int[item.rarity],
                                        "path": f'/resources/sprites/{item.metatype}s/{item.metaid}.png',
                                        "title": f"{itemmeta['name']}",
                                        "item": f'Looted by [{pcsquad.id}] {pcsquad.name}',
                                        "footer": f'NB: This item is [{item.bound_type}]'},
                            "embed": True,
                            "scope": f'Squad-{pc.squad}'}
                    yqueue_put('yarqueue:discord', qmsg)
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (False,
                f'[SQL] Loot update failed (pcid:{pc.id})')
    else:
        return (True, None)
    finally:
        session.close()

def fn_creature_stats_add(creature,metaRace,pcclass):
    session = Session()

    try:
        stats = CreatureStats(id     = creature.id,
                              m_race = metaRace['min_m'],
                              r_race = metaRace['min_r'],
                              g_race = metaRace['min_g'],
                              v_race = metaRace['min_v'],
                              p_race = metaRace['min_p'],
                              b_race = metaRace['min_b'])

        if pcclass == '1': stats.m_class = 10
        if pcclass == '2': stats.r_class = 10
        if pcclass == '3': stats.g_class = 10
        if pcclass == '4': stats.v_class = 10
        if pcclass == '5': stats.p_class = 10
        if pcclass == '6': stats.b_class = 10

        session.add(stats)
        session.commit()
        session.refresh(stats)
    except Exception as e:
        session.rollback()
        logger.error(f'Stats Query KO [{e}]')
        return None
    else:
        if stats:
            return stats
        else:
            return None
    finally:
        session.close()

def fn_creature_stats_del(creature):
    session = Session()

    try:
        stats = session.query(CreatureStats)\
                       .filter(CreatureStats.id == creature.id)\
                       .one_or_none()

        if stats: session.delete(stats)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Stats Query KO [{e}]')
        return None
    else:
        return True
    finally:
        session.close()

def fn_creature_stats_get(creature):
    session = Session()

    try:
        stats = session.query(CreatureStats)\
                       .filter(CreatureStats.id == creature.id)\
                       .one_or_none()
    except Exception as e:
        logger.error(f'Stats Query KO [{e}]')
        return None
    else:
        return stats
    finally:
        session.close()

def fn_creature_position_set(creatureid,x,y):
    session = Session()

    try:
        creature = session.query(Creature)\
                          .filter(Creature.id == creatureid)\
                          .one_or_none()

        if creature:
            creature.x = x
            creature.y = y
        else:
            logger.warning(f'Creature Query KO - Creature Not Found (creatureid:{creatureid})')

        session.commit()
        session.refresh(creature)
    except Exception as e:
        session.rollback()
        logger.error(f'Creature Query KO [{e}]')
        return None
    else:
        if creature:
            return creature
        else:
            return None
    finally:
        session.close()
