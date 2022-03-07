# -*- coding: utf8 -*-

from random                  import randint

from ..session               import Session
from ..models                import (Creature,
                                     Item)

from .fn_creature            import *
from .fn_user                import fn_user_get
from .fn_wallet              import fn_wallet_ammo_get,fn_wallet_ammo_set

from nosql.models.RedisPa    import *

# To accessing dict keys like an attribute
# Might refactor and use dataclasses instead
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

# Loading the Meta for later use
try:
    metaWeapons = metas.get_meta('weapon')
    metaArmors  = metas.get_meta('armor')
except Exception as e:
    logger.error(f'Meta fectching: KO [{e}]')
else:
    logger.trace(f'Meta fectching: OK')

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

    creature_pa = RedisPa.get(pc)
    bluepa      = creature_pa['blue']['pa']
    redpa       = creature_pa['red']['pa']

    for coords in path:
        x,y        = map(int, coords.strip('()').split(','))
        if abs(pc.x - x) <= 1 and abs(pc.y - y) <= 1:
            if bluepa >= 3:
                # Enough PA to move ONLY on blue 🔵 PA
                bluepa     -= 3
                pc   = session.query(Creature).filter(Creature.id == pcid).one_or_none()
                pc.x = x
                pc.y = y
            elif 0 < bluepa < 3 and redpa >= 1:
                # Enough PA to move on blue 🔵 + red 🔴 PA
                redpa      -= (3 - bluepa)
                bluepa      = 0
                pc   = session.query(Creature).filter(Creature.id == pcid).one_or_none()
                pc.x = x
                pc.y = y
            elif bluepa == 0 and redpa >= 3:
                # Enough PA to move ONLY on red 🔴 PA
                redpa     -= 3
                pc   = session.query(Creature).filter(Creature.id == pcid).one_or_none()
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
        RedisPa.set(pc,0,8 - bluepa) # We consume the blue 🔵 PA
        RedisPa.set(pc,16 - redpa,0)  # We consume the red  🔴 PA
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

        return (200, True, 'PC successfully moved', RedisPa.get(pc))
    finally:
        session.close()

# API: /mypc/<int:pcid>/action/attack/<int:weaponid>/<int:targetid>
def mypc_action_attack(username,pcid,weaponid,targetid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    tg          = fn_creature_get(None,targetid)[3]
    creature_pa = RedisPa.get(pc)

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
            # We grab the weapon wanted from metaWeapons
            metaWeapon = dict(list(filter(lambda x:x["id"] == item.metaid,metaWeapons))[0]) # Gruikfix
        except Exception as e:
            return (200,
                    False,
                    f'[SQL] Item query failed (pcid:{pc.id},weaponid:{weaponid}) [{e}]',
                    None)
        else:
            # Make it persistent after session.close()
            session.expunge(item)
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

    if metaWeapon['ranged'] is False:
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
        if abs(pc.x - tg.x) > metaWeapon['rng'] or abs(pc.y - tg.y) > metaWeapon['rng']:
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
    if creature_pa['red']['pa'] < itemmeta.pas_use:
        # Not enough PA to attack
        return (200,
                False,
                'Not enough PA to attack',
                {"red": creature_pa['red'],
                 "blue": creature_pa['blue'],
                 "action": None})
    else:
        # Enough PA to attack, we consume the red PAs
        incr_hs(pc,'action:attack',1) # Redis HighScore
        RedisPa.set(pc,itemmeta.pas_use,0)

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
            {"red": RedisPa.get(pc)['red'],
             "blue": RedisPa.get(pc)['blue'],
             "action": action})

# API: /mypc/<int:pcid>/action/reload/<int:weaponid>
def mypc_action_reload(username,pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()
    redpa       = RedisPa.get(pc)['red']['pa']

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pc.id},username:{username})',
                None)

    # Retrieving weapon stats
    try:
        item     = session.query(Item)\
                          .filter(Item.id == weaponid, Item.bearer == pc.id)\
                          .one_or_none()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Query failed (pcid:{pc.id},weaponid:{weaponid}) [{e}]',
                None)
    else:
        if item is None:
            return (200,
                    False,
                    f'Item not found (pcid:{pc.id},weaponid:{weaponid})',
                    None)

    itemmeta = dict(list(filter(lambda x:x["id"]==item.metaid,metaWeapons))[0]) # Gruikfix
    if itemmeta is None:
        return (200,
                False,
                f'ItemMeta not found (pcid:{pcid},weaponid:{item.id})',
                None)
    if itemmeta['pas_reload'] is None:
        return (200,
                False,
                f'Item is not reloadable (pcid:{pc.id},weaponid:{item.id})',
                None)
    if item.ammo == itemmeta['max_ammo']:
        return (200,
                False,
                f'Item is already loaded (pcid:{pc.id},weaponid:{item.id})',
                None)

    if redpa < itemmeta['pas_reload']:
        # Not enough PA to reload
        return (200,
                False,
                'Not enough PA to reload',
                {"red": RedisPa.get(pc)['red'],
                 "blue": RedisPa.get(pc)['blue'],
                 "action": None})
    else:
        # Enough PA to reload, we consume the red PAs
        RedisPa.set(pc,itemmeta['pas_reload'],0)

    walletammo = fn_wallet_ammo_get(pc,item,itemmeta['caliber'])
    neededammo = itemmeta['max_ammo'] - item.ammo
    if walletammo < neededammo:
        # Not enough ammo to reload
        return (200,
                False,
                'Not enough ammo to reload',
                None)
    else:
        # Enough ammo to reload, we remove the ammo from wallet
        # The '* -1' is to negate the number as the fn_set() is doing an addition
        fn_wallet_ammo_set(pc,itemmeta['caliber'],neededammo * -1)

    try:
        item       = session.query(Item)\
                            .filter(Item.id == weaponid, Item.bearer == pc.id)\
                            .one_or_none()
        item.ammo += neededammo
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Weapon reload failed (pcid:{pc.id},weaponid:{item.id}) [{e}]',
                None)
    else:
        incr.one(f'highscores:{pc.id}:action:reload')
        return (200,
                True,
                f'Weapon reload successed (pcid:{pc.id},weaponid:{item.id})',
                RedisPa.get(pc))
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/action/unload/<int:weaponid>
def mypc_action_unload(username,pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pc.id},username:{username})',
                None)

    # Retrieving weapon stats
    try:
        item     = session.query(Item)\
                          .filter(Item.id == weaponid, Item.bearer == pc.id)\
                          .one_or_none()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Query failed (pcid:{pc.id},weaponid:{weaponid}) [{e}]',
                None)
    else:
        if item is None:
            return (200,
                    False,
                    f'Item not found (pcid:{pc.id},weaponid:{weaponid})',
                    None)
        if item.ammo == 0:
            return (200,
                    False,
                    f'Item is already empty (pcid:{pc.id},weaponid:{weaponid})',
                    None)

    itemmeta = dict(list(filter(lambda x:x["id"]==item.metaid,metaWeapons))[0]) # Gruikfix
    if itemmeta is None:
        return (200,
                False,
                f'ItemMeta not found (pcid:{pc.id},weaponid:{item.id})',
                None)
    if itemmeta['pas_reload'] is None:
        return (200,
                False,
                f'Item is not reloadable (pcid:{pc.id},weaponid:{item.id})',
                None)

    if RedisPa.get(pc)['blue']['pa'] < 2:
        # Not enough PA to unload
        return (200,
                False,
                'Not enough PA to unload',
                {"red": RedisPa.get(pc)['red'],
                 "blue": RedisPa.get(pc)['blue'],
                 "action": None})
    else:
        # Enough PA to unload, we consume the red PAs
        RedisPa.set(pc,0,2)

    ret = fn_wallet_ammo_set(pc,itemmeta['caliber'],item.ammo)
    if ret is None:
        return (200,
                True,
                f'Weapon unload failed (pcid:{pcid},weaponid:{item.id})',
                RedisPa.get(pc))

    try:
        item       = session.query(Item)\
                            .filter(Item.id == weaponid, Item.bearer == pc.id)\
                            .one_or_none()
        item.ammo  = 0
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Weapon unload failed (pcid:{pc.id},weaponid:{weaponid}) [{e}]',
                None)
    else:
        incr.one(f'highscores:{pc.id}:action:unload')
        # We create the Creature Event
        events.set_event(pc.id,
                         None,
                         'action',
                         'Unloaded a weapon',
                         30*86400)
        return (200,
                True,
                f'Weapon unload successed (pcid:{pc.id},weaponid:{weaponid})',
                RedisPa.get(pc))
    finally:
        session.close()
