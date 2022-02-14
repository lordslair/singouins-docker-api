# -*- coding: utf8 -*-

import dataclasses

from datetime            import datetime

from ..session           import Session
from ..models            import (Creature,
                                 CreatureSlots,
                                 CreatureStats,
                                 Item,
                                 Wallet)

from ..utils.loot        import *
from ..utils.redis.metas import get_meta
from ..utils.redis.stats import (get_hp,
                                 set_hp,
                                 set_stats)

from .fn_global          import clog

# Loading the Meta for later use
try:
    metaWeapons = get_meta('weapon')
except Exception as e:
    print(f'[Redis:get_meta()] meta fetching failed [{e}]')

def fn_creature_get(pcname,pcid):
    session = Session()

    try:
        if pcid:
            pc = session.query(Creature).filter(Creature.id == pcid).one_or_none()
        elif pcname:
            pc = session.query(Creature).filter(Creature.name == pcname).one_or_none()
        else:
            return (200,
                    False,
                    f'Wrong pcid/pcname (pcid:{pcid},pcname:{pcname})',
                    None)
    except Exception as e:
        return (200,
                False,
                f'[SQL] PC query failed (pcid:{pcid},pcname:{pcname}) [{e}]',
                None)
    else:
        if pc:
            return (200,
                    True,
                    f'PC successfully found (pcid:{pcid},pcname:{pcname})',
                    pc)
        else:
            return (200,
                    False,
                    f'PC does not exist (pcid:{pcid},pcname:{pcname})',
                    None)
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
        clog(tg.id,None,f'Targeted by {pc.name}')
        session.close()

def fn_creature_wound(pc,tg,dmg):
    session = Session()
    try:
        tg      = session.query(Creature).filter(Creature.id == tg.id).one_or_none()
        tg.hp   = tg.hp - dmg    # We update Health Points
        tg.date = datetime.now() # We update date
        session.commit()
    except Exception as e:
        return (200, False, 'HP update failed', None)
    else:
        clog(tg.id,None,'Suffered minor injuries')
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

        clog(pc.id,tgid,f'Killed {tgname}')
        clog(tgid,None,'Died')
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
        clog(pc.id,None,'Gained Loot')
        return (True, None)
    finally:
        session.close()

def fn_creature_stats(pc):
    session      = Session()
    stats_items  = {"off":{
                            "capcom": 0,
                            "capsho": 0},
                    "def":{
                            "armor": {
                                        "p": 0,
                                        "b": 0},
                            "hpmax": 0,
                            "hp": 0,
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
            armors     = [feet,
                          hands,
                          head,
                          shoulders,
                          torso,
                          legs]

            for armor in armors:
                if armor is not None:
                    metaWeapon = dict(list(filter(lambda x:x["id"] == armor.metaid,metaWeapons))[0]) # Gruikfix
                    armormetas.append(metaWeapon)

            # We grab the weapon wanted from metaWeapons
            # TODO

        # We need to query Creature base stats
        cs        = session.query(CreatureStats)\
                           .filter(CreatureStats.id == pc.id)\
                           .one_or_none()

    except Exception as e:
        print(e)
    else:
        for meta in armormetas:
            if meta:
                stats_items['def']['armor']['b'] += meta['arm_b']
                stats_items['def']['armor']['p'] += meta['arm_p']

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

        # About HP
        hpmax = 100 + base_m + round(pc.level/2)
        hp    = get_hp(pc)
        if hp:
            pass # Meaning key was already populated
        else:
            set_hp(pc,hpmax)
            hp = hpmax

        # We push data in final dict
        stats  = {"base":{
                            "m": 0 + base_m,
                            "r": 0 + base_r,
                            "g": 0 + base_g,
                            "v": 0 + base_v,
                            "p": 0 + base_p,
                            "b": 0 + base_b},
                  "off":{
                            "capcom": round((base_g + round((base_m + base_r)/2))/2),
                            "capsho": round((base_v + round((base_b + base_r)/2))/2)},
                  "def":{
                            "armor": {
                                        "p": 0 + stats_items['def']['armor']['p'],
                                        "b": 0 + stats_items['def']['armor']['b']},
                            "hpmax": hpmax,
                            "hp": hp,
                            "dodge": base_r,
                            "parry": round(((base_g-100)/50) * ((base_m-100)/50))}}

        # Data was not in Redis, so we push it
        set_stats(pc,stats)

        # To avoid errors, we return the freshly computed value
        return (stats)
    finally:
        session.close()
