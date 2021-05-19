# -*- coding: utf8 -*-

from random             import randint

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_user           import fn_user_get
from .fn_wallet         import fn_wallet_ammo_get,fn_wallet_ammo_set
from .fn_global         import clog

# To accessing dict keys like an attribute
# Might refactor and use dataclasses instead
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

#
# Queries /mypc/{pcid}/action/*
#

# API: /mypc/<int:pcid>/action/move/<int:itemid>/give/<int:targetid>
def mypc_action_move(username,pcid,path):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()

    (oldx,oldy) = pc.x,pc.y

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    pa         = get_pa(pcid)[3]
    bluepa     = pa['blue']['pa']
    redpa      = pa['red']['pa']

    for coords in path:
        x,y        = map(int, coords.strip('()').split(','))
        if abs(pc.x - x) <= 1 and abs(pc.y - y) <= 1:
            if bluepa >= 3:
                # Enough PA to move ONLY on blue 🔵 PA
                bluepa     -= 3
                pc   = session.query(PJ).filter(PJ.id == pcid).one_or_none()
                pc.x = x
                pc.y = y
            elif 0 < bluepa < 3 and redpa >= 1:
                # Enough PA to move on blue 🔵 + red 🔴 PA
                redpa      -= (3 - bluepa)
                bluepa      = 0
                pc   = session.query(PJ).filter(PJ.id == pcid).one_or_none()
                pc.x = x
                pc.y = y
            elif bluepa == 0 and redpa >= 3:
                # Enough PA to move ONLY on red 🔴 PA
                redpa     -= 3
                pc   = session.query(PJ).filter(PJ.id == pcid).one_or_none()
                pc.x = x
                pc.y = y

    try:
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] Coords update failed (pcid:{pcid},path:{path})',
                None)
    else:
        set_pa(pcid,0,8 - bluepa) # We consume the blue 🔵 PA
        set_pa(pcid,16 - redpa,0)  # We consume the red  🔴 PA
        # We put the info in queue for ws
        qciphered = False
        qpayload  = {"id": pc.id, "x": x, "y": y}
        qscope    = {"id": None, "scope": 'broadcast'}
        qmsg = {"ciphered": qciphered,
                "payload": qpayload,
                "route": "mypc/{id1}/action/move",
                "scope": qscope}
        yqueue_put('broadcast', qmsg)
        incr_hs(pc,'action:move', 1) # Redis HighScore

        clog(pc.id,None,'Moved from ({},{}) to ({},{})'.format(oldx,oldy,x,y))
        return (200, True, 'PC successfully moved', get_pa(pcid)[3])
    finally:
        session.close()

# API: /mypc/<int:pcid>/action/attack/<int:weaponid>/<int:targetid>
def mypc_action_attack(username,pcid,weaponid,targetid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    tg          = fn_creature_get(None,targetid)[3]
    pa          = get_pa(pcid)[3]

    action = {"failed": True,
              "hit": False,
              "critical": False,
              "damages": None,
              "killed": False}

    # Check if target exists
    if tg is None:
        return (200,
                False,
                f'Target does not exists (targetid:{targetid})',
                action)

    # Check if target is taggued
    if tg.targeted_by is not None:
        # Target already taggued by a pc
        (code, success, msg, tag) = fn_creature_get(None,tg.targeted_by)
        if tag.id != pc.id and tag.squad != pc.squad:
            # Target not taggued by the pc itself
            # Target not taggued by a pc squad member
            return (200,
                    False,
                    f'Target does not belong to the PC/Squad (targeted_by:{tg.targeted_by})',
                    None)

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    if weaponid == 0:
        item     = AttrDict()
        itemmeta = AttrDict()
        itemmeta.ranged   = False
        itemmeta.pas_use  = 4
        itemmeta.dmg_base = 20
    else:
        session     = Session()
        try:
            # Retrieving weapon stats
            item     = session.query(Item).filter(Item.id == weaponid, Item.bearer == pc.id).one_or_none()
            itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == item.metaid).one_or_none()
        except Exception as e:
            return (200,
                    False,
                    f'[SQL] Item query failed (pcid:{pc.id},weaponid:{weaponid}) [{e}]',
                    None)
        else:
            # Make it persistent after session.close()
            session.expunge(item)
            session.expunge(itemmeta)
            # Check if item exists/is owned by PC
            if item is None:
                return (200,
                        False,
                        f'Weapon does not exists/not belong to PC (pcid:{pc.id},weaponid:{weaponid})',
                        action)
        finally:
            session.close()

    if item is None:
        return (200,
                False,
                f'Item not found (pcid:{pc.id},weaponid:{weaponid})',
                None)
    if itemmeta is None:
        return (200,
                False,
                f'ItemMeta not found (pcid:{pc.id},weaponid:{weaponid})',
                None)

    if itemmeta.ranged is False:
        # Checking distance for contact weapons
        if abs(pc.x - tg.x) > 1 or abs(pc.y - tg.y) > 1:
            # Target is not on a adjacent tile
            return (200,
                    False,
                    f'Target is out of range (pcid:{pcid},targetid:{targetid})',
                    None)
        # Combat Capacity (Contact weapons)
        pc.capacity  = (pc.g + (pc.m + pc.r)/2 )/2
        pc.dmg_bonus = (100 + (pc.g - 100)/3)/100
        tg.avoid     = tg.r
        tg.armor     = tg.arm_p

        rpath = 'contact' # Used for Redis HighScore path
    else:
        # Checking distance for ranged weapons
        if abs(pc.x - tg.x) > itemmeta.rng or abs(pc.y - tg.y) > itemmeta.rng:
            # Target is not in range
            return (200,
                    False,
                    f'Target is out of range (pcid:{pcid},targetid:{targetid})',
                    action)
        # Shooting capacity (Ranged weapons)
        pc.capacity   = (pc.v + (pc.b + pc.r)/2 )/2
        pc.dmg_bonus  = (100 + (pc.v - 100)/3)/100
        tg.avoid      = tg.r
        tg.armor      = tg.arm_b

        rpath = 'range' # Used for Redis HighScore path

        # Checking ammo
        if item.ammo < 1:
            return (200,
                    False,
                    'Not enough Ammo to attack',
                    {"red": pa['red'],
                     "blue": pa['blue'],
                     "action": None})
        else:
            item.ammo -= 1 # /!\ item was expunged earlier

    if randint(1, 100) > 97:
        # Failed action
        incr_hs(pc,f'combat:given:{rpath}:fails',1) # Redis HighScore
    else:
        # Successfull action
        action['failed'] = False

    # At this point, we consider that the attack can happen, and manage the PA
    # Check it PC has enough PA
    if pa['red']['pa'] < itemmeta.pas_use:
        # Not enough PA to attack
        return (200,
                False,
                'Not enough PA to attack',
                {"red": pa['red'],
                 "blue": pa['blue'],
                 "action": None})
    else:
        # Enough PA to attack, we consume the red PAs
        incr_hs(pc,'action:attack',1) # Redis HighScore
        set_pa(pcid,itemmeta.pas_use,0)

    if pc.capacity > tg.avoid:
        # Successfull attack
        action['hit'] = True
        # The target is now acquired to the attacker
        if tg.targeted_by is None:
            fn_creature_tag(pc,tg)
        incr_hs(pc,f'combat:given:{rpath}:hits',1) # Redis HighScore
    else:
        # Failed attack
        pass

    if randint(1, 100) <= 5:
        # The attack is a critical Hit
        pc.dmg_crit = round(150 + pc.r / 10)
    else:
        # The attack is a normal Hit
        pc.dmg_crit = 100

    dmg_raw = round(itemmeta.dmg_base * pc.dmg_bonus * pc.dmg_crit / 100)
    dmg     = dmg_raw - tg.armor

    incr_hs(pc,f'combat:given:{rpath}:damages',dmg_raw)    # Redis HighScore
    incr_hs(tg,f'combat:received:{rpath}:damages',dmg_raw) # Redis HighScore

    if dmg > 0:
        # The attack deals damage
        action['damages'] = dmg
        incr_hs(pc,f'combat:given:{rpath}:wounds',dmg)    # Redis HighScore
        incr_hs(tg,f'combat:received:{rpath}:wounds',dmg) # Redis HighScore

        if tg.hp - dmg >= 0:
            # The attack wounds
            fn_creature_wound(pc,tg,dmg)
        else:
            # The attack kills
            action['killed'] = True
            incr_hs(pc,'combat:kills',1)        # Redis HighScore
            incr_hs(tg,'combat:deaths',1)       # Redis HighScore
            incr_hs(pc,f'bestiary:{tg.race}',1) # Redis HighScore
            fn_creature_kill(pc,tg,action)

            # Experience points are generated
            (ret,msg) = fn_creature_gain_xp(pc,tg)
            if ret is not True:
                return (200, False, msg, None)

            # Loots are given to PCs
            (ret,msg) = fn_creature_gain_loot(pc,tg)
            if ret is not True:
                return (200, False, msg, None)
    else:
        # The attack does not deal damage
        pass

    return (200,
            True,
            'Target successfully attacked',
            {"red": get_pa(pcid)[3]['red'],
             "blue": pa['blue'],
             "action": action})

# API: /mypc/<int:pcid>/action/reload/<int:weaponid>
def mypc_action_reload(username,pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()
    redpa       = get_pa(pcid)[3]['red']['pa']

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    # Pre-flight checks
    item     = session.query(Item).filter(Item.id == weaponid, Item.bearer == pc.id).one_or_none()
    if item is None:
        return (200,
                False,
                'Item not found (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)

    itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == item.metaid).one_or_none()
    if itemmeta is None:
        return (200,
                False,
                'ItemMeta not found (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)
    session.expunge(itemmeta)
    if itemmeta.pas_reload is None:
        return (200,
                False,
                'Item is not reloadable (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)

    if item.ammo == itemmeta.max_ammo:
        return (200,
                False,
                'Item is already loaded (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)

    if redpa < itemmeta.pas_reload:
        # Not enough PA to reload
        return (200,
                False,
                'Not enough PA to reload',
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "action": None})
    else:
        # Enough PA to reload, we consume the red PAs
        set_pa(pc.id,itemmeta.pas_reload,0)

    walletammo = fn_wallet_ammo_get(pc,item,itemmeta)
    neededammo = itemmeta.max_ammo - item.ammo
    if walletammo < neededammo:
        # Not enough ammo to reload
        return (200,
                False,
                'Not enough ammo to reload',
                None)
    else:
        # Enough ammo to reload, we remove the ammo from wallet
        # The '* -1' is to negate the number as the fn_set() is doing an addition
        fn_wallet_ammo_set(pc,itemmeta.caliber,neededammo * -1)

    try:
        item       = session.query(Item).filter(Item.id == weaponid, Item.bearer == pc.id).one_or_none()
        item.ammo += neededammo
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Weapon reload failed (pcid:{},weaponid:{})'.format(pc.id,item.id),
                None)
    else:
        incr_hs(pc,'action:reload',1) # Redis HighScore
        return (200,
                True,
                'Weapon reload success (pcid:{},weaponid:{})'.format(pc.id,item.id),
                get_pa(pcid)[3])
    finally:
        session.close()

# API: /mypc/<int:pcid>/action/unload/<int:weaponid>
def mypc_action_unload(username,pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    # Retrieving weapon stats
    item     = session.query(Item).filter(Item.id == weaponid, Item.bearer == pc.id).one_or_none()
    itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == item.metaid).one_or_none()
    session.expunge(itemmeta)

    # Pre-flight checks
    if item is None:
        return (200,
                False,
                'Item not found (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)
    if itemmeta is None:
        return (200,
                False,
                'ItemMeta not found (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)
    if item.ammo == 0:
        return (200,
                False,
                'Item is already empty (pcid:{},weaponid:{})'.format(pcid,weaponid),
                None)

    if get_pa(pcid)[3]['blue']['pa'] < 2:
        # Not enough PA to unload
        return (200,
                False,
                'Not enough PA to unload',
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "action": None})
    else:
        # Enough PA to unload, we consume the red PAs
        set_pa(pc.id,0,2)

    ret = fn_wallet_ammo_set(pc,itemmeta.caliber,item.ammo)
    if ret is None:
        return (200,
                True,
                'Weapon unload failed (pcid:{},weaponid:{})'.format(pc.id,item.id),
                get_pa(pcid)[3])

    try:
        item       = session.query(Item).filter(Item.id == weaponid, Item.bearer == pc.id).one_or_none()
        item.ammo  = 0
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Weapon unload failed (pcid:{},weaponid:{})'.format(pc.id,weaponid),
                None)
    else:
        incr_hs(pc,'action:unload',1) # Redis HighScore
        clog(pc.id,None,'Unloaded a weapon')
        return (200,
                True,
                'Weapon unload success (pcid:{},weaponid:{})'.format(pc.id,weaponid),
                get_pa(pcid)[3])
    finally:
        session.close()
