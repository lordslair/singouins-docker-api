# -*- coding: utf8 -*-

from random             import randint

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_highscore      import *
from .fn_user           import fn_user_get
from .fn_global         import clog

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

    for coords in path:
        bluepa                   = get_pa(pcid)[3]['blue']['pa']
        x,y                      = map(int, coords.strip('()').split(','))

        if abs(pc.x - x) <= 1 and abs(pc.y - y) <= 1:
            if bluepa > 1:
                # Enough PA to move
                set_pa(pcid,0,1) # We consume the blue PA (1) right now
                pc   = session.query(PJ).filter(PJ.id == pcid).one_or_none()
                pc.x = x
                pc.y = y

    try:
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Coords update failed (pcid:{},path:{})'.format(pcid,path),
                None)
    else:
        clog(pc.id,None,'Moved from ({},{}) to ({},{})'.format(oldx,oldy,x,y))
        return (200, True, 'PC successfully moved', get_pa(pcid)[3])
    finally:
        session.close()

# API: /mypc/<int:pcid>/action/attack/<int:weaponid>/<int:targetid>
def mypc_action_attack(username,pcid,weaponid,targetid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    tg          = fn_creature_get(None,targetid)[3]
    session     = Session()

    if tg.targeted_by is not None:
        # Target already taggued by a pc
        (code, success, msg, tag) = fn_creature_get(None,tg.targeted_by)
        if tag.id != pc.id and tag.squad != pc.squad:
            # Target not taggued by the pc itself
            # Target not taggued by a pc squad member
            return (200, False, 'Target does not belong to the PC/Squad', None)

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    tg     = fn_creature_get(None,targetid)[3]
    redpa  = get_pa(pcid)[3]['red']['pa']
    action = {"failed": True,
              "hit": False,
              "critical": False,
              "damages": None,
              "killed": False}

    if weaponid == 0:
        item     = AttrDict()
        itemmeta = AttrDict()
        itemmeta.ranged   = False
        itemmeta.pas_use  = 4
        itemmeta.dmg_base = 20
    else:
        # Retrieving weapon stats
        item     = session.query(Item).filter(Item.id == weaponid, Item.bearer == pc.id).one_or_none()
        itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == item.metaid).one_or_none()
        session.expunge(itemmeta)

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

    if itemmeta.ranged is False:
        # Checking distance for contact weapons
        if abs(pc.x - tg.x) > 1 or abs(pc.y - tg.y) > 1:
            # Target is not on a adjacent tile
            return (200,
                    False,
                    'Target is not on contact',
                    None)
        # Combat Capacity (Contact weapons)
        pc.capacity  = (pc.g + (pc.m + pc.r)/2 )/2
        pc.dmg_bonus = (100 + (pc.g - 100)/3)/100
        tg.avoid     = tg.r
        tg.armor     = tg.arm_p
    else:
        # Checking distance for ranged weapons
        if abs(pc.x - tg.x) > itemmeta.rng or abs(pc.y - tg.y) > itemmeta.rng:
            # Target is not on a adjacent tile
            return (200,
                    False,
                    'Target is out of range',
                    None)
        # Shooting capacity (Ranged weapons)
        pc.capacity   = (pc.v + (pc.b + pc.r)/2 )/2
        pc.dmg_bonus  = (100 + (pc.v - 100)/3)/100
        tg.avoid      = tg.r
        tg.armor      = tg.arm_b

    if redpa < itemmeta.pas_use:
        # Not enough PA to attack
        return (200,
                False,
                'Not enough PA to attack',
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "action": None})
    else:
        # Enough PA to attack, we consume the red PAs
        set_pa(pcid,itemmeta.pas_use,0)

    if itemmeta.ranged is True:
        if item.ammo < 1:
            return (200,
                    False,
                    'Not enough Ammo to attack',
                    {"red": get_pa(pcid)[3]['red'],
                     "blue": get_pa(pcid)[3]['blue'],
                     "action": None})
        else:
            item.ammo -= 1

    if randint(1, 100) > 97:
        # Failed action
        clog(pc.id,None,'Failed an attack')
    else:
        # Successfull action
        action['failed'] = False

    if pc.capacity > tg.avoid:
        # Successfull attack
        action['hit'] = True
        # The target is now acquired to the attacker
        fn_creature_tag(pc,tg)
    else:
        # Failed attack
        clog(pc.id,tg.id,'Missed {}'.format(tg.name))
        clog(tg.id,None,'Avoided {}'.format(pc.name))

    if randint(1, 100) <= 5:
        # The attack is a critical Hit
        pc.dmg_crit = round(150 + pc.r / 10)
        clog(pc.id,tg.id,'Critically Attacked {}'.format(tg.name))
        clog(tg.id,None,'Critically Hit by {}'.format(pc.name))
    else:
        # The attack is a normal Hit
        pc.dmg_crit = 100
        clog(pc.id,tg.id,'Attacked {}'.format(tg.name))
        clog(tg.id,None,'Hit by {}'.format(pc.name))

    dmg = round(itemmeta.dmg_base * pc.dmg_bonus * pc.dmg_crit / 100) - tg.armor

    if dmg > 0:
        # The attack deals damage
        action['damages'] = dmg

        if tg.hp - dmg >= 0:
            # The attack wounds
            fn_creature_wound(pc,tg,dmg)
        else:
            # The attack kills
            action['killed'] = True
            fn_creature_kill(pc,tg)

            # HighScores points are generated
            (ret,msg) = fn_highscore_kill_set(pc)
            if ret is not True:
                return (200, False, msg, None)

            # Experience points are generated
            (ret,msg) = fn_creature_gain_xp(pc,tg)
            if ret is not True:
                return (200, False, msg, None)

            # Loots are given to PCs
            (ret,msg) = fn_creature_gain_loot(pc,tg)
            if ret is not True:
                return (200, False, msg, None)
    else:
        clog(tg.id,None,'Suffered no injuries')
        # The attack does not deal damage

    return (200,
            True,
            'Target successfully attacked',
            {"red": get_pa(pcid)[3]['red'],
             "blue": get_pa(pcid)[3]['blue'],
             "action": action})

# API: /mypc/<int:pcid>/action/reload/<int:weaponid>
def mypc_action_reload(username,pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()
    redpa       = get_pa(pcid)[3]['red']['pa']

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

    try:
        item.ammo = itemmeta.max_ammo
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Weapon reload failed (pcid:{},weaponid:{})'.format(pc.id,item.id),
                None)
    else:
        clog(pc.id,None,'Reloaded a weapon')
        return (200,
                True,
                'Weapon reload success (pcid:{},weaponid:{})'.format(pc.id,itemid),
                get_pa(pcid)[3])
    finally:
        session.close()
