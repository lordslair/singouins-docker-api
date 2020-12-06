# -*- coding: utf8 -*-

from random             import randint

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_highscore      import *
from .fn_user           import fn_user_get
from .fn_global         import clog

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
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    (code, success, msg, tg) = fn_creature_get(None,targetid)

    if tg.targeted_by is not None:
        # Target already taggued by a pc
        (code, success, msg, tag) = fn_creature_get(None,tg.targeted_by)
        if tag.id != pc.id and tag.squad != pc.squad:
            # Target not taggued by the pc itself
            # Target not taggued by a pc squad member
            return (200, False, 'Target does not belong to the PC/Squad', None)

    if pc and pc.account == user.id:
        if weaponid == 0:
            (code, success, msg, tg) = fn_creature_get(None,targetid)
            redpa                    = get_pa(pcid)[3]['red']['pa']
            dmg_wp                   = 20
            action                   = {"failed": True, "hit": False, "critical": False, "damages": None, "killed": False}

            if abs(pc.x - tg.x) <= 1 and abs(pc.y - tg.y) <= 1:
                # Target is on a adjacent tile
                if redpa > 1:
                    # Enough PA to attack
                    set_pa(pcid,4,0) # We consume the red PA (4) right now
                    pc.comcap  = (pc.g + (pc.m + pc.r)/2 )/2

                    if randint(1, 100) <= 97:
                        # Successfull action
                        action['failed'] = False
                        if pc.comcap > tg.r:
                            # The attack successed
                            action['hit'] = True

                            # The target is now acquired to the attacker
                            fn_creature_tag(pc,tg)

                            if randint(1, 100) <= 5:
                                # The attack is a critical Hit
                                dmg_crit = round(150 + pc.r / 10)
                                clog(pc.id,tg.id,'Critically Attacked {}'.format(tg.name))
                                clog(tg.id,None,'Critically Hit by {}'.format(pc.name))
                            else:
                                # The attack is a normal Hit
                                dmg_crit = 100
                                clog(pc.id,tg.id,'Attacked {}'.format(tg.name))
                                clog(tg.id,None,'Hit by {}'.format(pc.name))

                            dmg = round(dmg_wp * dmg_crit / 100) - tg.arm_p
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
                        else:
                            # The attack missed
                            clog(pc.id,tg.id,'Missed {}'.format(tg.name))
                            clog(tg.id,None,'Avoided {}'.format(pc.name))
                    else:
                        # Failed action
                        clog(pc.id,None,'Failed an attack')
                else:
                    # Not enough PA to attack
                    return (200,
                            False,
                            'Not enough PA to attack',
                            {"red": get_pa(pcid)[3]['red'],
                             "blue": get_pa(pcid)[3]['blue'],
                             "action": None})
            else:
                # Target is too far
                return (200, False, 'Coords incorrect', None)
        return (200,
                True,
                'Target successfully attacked',
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "action": action})
    else: return (409, False, 'Token/username mismatch', None)
