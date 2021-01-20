# -*- coding: utf8 -*-

from datetime       import datetime
from random         import randint

import textwrap

from ..session          import Session
from ..models           import *
from ..utils.loot       import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_user           import *
from .fn_highscore      import *
from .fn_global         import clog

#
# Queries: /pc
#
from variables      import PCS_URL

def get_pc_exists(pcname,pcid):
    session = Session()

    try:
        if not pcname and not pcid:
            return False
        elif pcname and pcid:
            result = session.query(PJ).filter(PJ.name == pcname, PJ.id == pcid).one_or_none()
        elif pcname and not pcid:
            result = session.query(PJ).filter(PJ.name == pcname).one_or_none()
        elif not pcname and pcid:
            result = session.query(PJ).filter(PJ.id == pcid).one_or_none()
        else:
            return False
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return True
    finally:
        session.close()

def get_pcs(username):
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

def del_pc(username,pcid):
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

        session.delete(pc)
        session.delete(equipment)
        session.delete(wallet)
        session.delete(highscore)
        session.delete(stats)

        items = session.query(Item).filter(Item.bearer == pc.id).all()
        if items:
            session.delete(items)

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

#
# Queries: /mp
#

def add_mp(username,src,dsts,subject,body):
    (code, success, msg, pcsrc) = fn_creature_get(None,src)
    user                        = fn_user_get(username)
    session                     = Session()

    if pcsrc:
        for dst in dsts:
            (code, success, msg, pcdst) = fn_creature_get(None,dst)
            if pcdst:
                mp = MP(src_id  = pcsrc.id,
                        src     = pcsrc.name,
                        dst_id  = pcdst.id,
                        dst     = pcdst.name,
                        subject = subject,
                        body    = body)
                session.add(mp)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (200,
                    False,
                    '[SQL] MP creation failed (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                    None)
        else:
            return (201,
                    True,
                    'MP successfully created (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                    None)
        finally:
            session.close()

    elif user.id != pcsrc.account:
        return (409, False, 'Token/username mismatch', None)
    else:
        return (200,
                False,
                'PC does not exist (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                None)

def get_mp(username,pcid,mpid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] MP query failed (pcid:{},mpid:{})'.format(pc.id,mpid),
                    None)
        else:
            if mp:
                return (200,
                        True,
                        'MP successfully found (pcid:{},mpid:{})'.format(pc.id,mpid),
                        mp)
            else:
                return (200, True, 'MP not found (pcid:{},mpid:{})'.format(pc.id,mpid), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def del_mp(username,pcid,mpid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
            if not mp: return (200, True, 'No MP found for this PC', None)
            session.delete(mp)
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] MP deletion failed', None)
        else:
            return (200, True, 'MP successfully deleted', None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def get_mps(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mps = session.query(MP).filter(MP.dst_id == pc.id).all()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] MPs query failed (pcid:{})'.format(pc.id), None)
        else:
            if mps:
                for mp in mps: mp.body = textwrap.shorten(mp.body, width=50, placeholder="...")
                return (200, True, 'MPs successfully found (pcid:{})'.format(pc.id), mps)
            else:
                return (200, True, 'No MP found (pcid:{})'.format(pc.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def get_mp_addressbook(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            addressbook = session.query(PJ).with_entities(PJ.id,PJ.name).all()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Addressbook query failed (pcid:{})'.format(pc.id), None)
        else:
            if addressbook:
                return (200, True, 'Addressbook successfully found (pcid:{})'.format(pc.id), addressbook)
            else:
                return (200, True, 'No Addressbook found (pcid:{})'.format(pc.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /meta
#

def get_meta_item(metatype):
    session = Session()

    try:
        if    metatype == 'weapon': meta = session.query(MetaWeapon).all()
        elif  metatype == 'armor':  meta = session.query(MetaArmor).all()
        else:  meta = None
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Meta query failed (metatype:{})'.format(metatype),
                None)
    else:
        if meta:
            return (200, True, 'OK', meta)
        else:
            return (200, False, 'Meta does not exist (metatype:{})'.format(metatype), None)
    finally:
        session.close()

#
# Queries /squad
#

def get_squad(username,pcid,squadid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        try:
            squad = session.query(Squad).\
                            filter(Squad.id == pc.squad).\
                            filter(PJ.id == pc.id)

            pc_is_member  = squad.filter(PJ.squad_rank != 'Pending').one_or_none()
            pc_is_pending = squad.filter(PJ.squad_rank == 'Pending').one_or_none()

            if pc_is_member:
                squad   = squad.session.query(Squad).filter(Squad.id == pc.squad).one_or_none()
                members = session.query(PJ).filter(PJ.squad == squad.id).filter(PJ.squad_rank != 'Pending').all()
                pending = session.query(PJ).filter(PJ.squad == squad.id).filter(PJ.squad_rank == 'Pending').all()
            elif pc_is_pending:
                squad   = squad.session.query(Squad).filter(Squad.id == pc.squad).one_or_none()

        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Squad query failed (pcid:{},squadid:{})'.format(pcid,squadid),
                    None)
        else:
            if pc_is_member:
                if squad:
                    if isinstance(members, list):
                        if isinstance(pending, list):
                            return (200,
                                    True,
                                    'Squad query successed (pcid:{},squadid:{})'.format(pcid,squadid),
                                    {"squad": squad, "members": members, "pending": pending})
            elif pc_is_pending:
                return (200,
                        True,
                        'PC is pending in a squad (pcid:{},squadid:{})'.format(pcid,squadid),
                        {"squad": squad})
            else: return (200,
                          False,
                          'PC is not in a squad (pcid:{},squadid:{})'.format(pcid,squadid),
                          None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def add_squad(username,pcid,squadname):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        if session.query(Squad).filter(Squad.name == squadname).one_or_none():
            return (409, False, 'Squad already exists', None)
        if pc.squad is not None:
            return (200,
                    False,
                    'Squad leader already in a squad (pcid:{},squadid:{})'.format(pc.id,squad.id),
                    None)

        squad = Squad(name    = squadname,
                      leader  = pc.id)
        session.add(squad)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Squad creation failed (pcid:{})'.format(pcid), None)

        # Squad created, let's assign the team creator in the squad
        pc            = session.query(PJ).filter(PJ.id == pcid).one_or_none()
        squad         = session.query(Squad).filter(Squad.leader == pc.id).one_or_none()
        pc.squad      = squad.id
        pc.squad_rank = 'Leader'

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Squad leader assignation failed (pcid:{},squadid:{})'.format(pc.id,squad.id),
                    None)
        else:
            return (201,
                    True,
                    'Squad successfully created (pcid:{},squadid:{})'.format(pc.id,squad.id),
                    squad)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def del_squad(username,leaderid,squadid):
    (code, success, msg, leader) = fn_creature_get(None,leaderid)
    user                         = fn_user_get(username)
    session                      = Session()

    if leader:
        if leader.squad != squadid:
            return (200, False, 'Squad request outside of your scope ({} =/= {})'.format(leader.squad,squadid), None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(leaderid), None)

    if leader and leader.account == user.id:
        try:
            squad = session.query(Squad).filter(Squad.leader == leader.id).one_or_none()
            if not squad: return (200, True, 'No Squad found for this PC (pcid:{})'.format(leader.id), None)

            count = session.query(PJ).filter(PJ.squad == squad.id).count()
            if count > 1: return (200, False, 'Squad not empty (squadid:{})'.format(squad.id), None)

            session.delete(squad)
            pc = session.query(PJ).filter(PJ.id == leader.id).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Squad deletion failed (squadid:{})'.format(squad.id), None)
        else:
            return (200, True, 'Squad successfully deleted (squadid:{})'.format(squad.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def invite_squad_member(username,leaderid,squadid,targetid):
    (code, success, msg, target) = fn_creature_get(None,targetid)
    (code, success, msg, leader) = fn_creature_get(None,leaderid)
    user                         = fn_user_get(username)
    session                      = Session()

    if leader:
        if leader.squad is None:
            return (200, False, 'PC is not in a squad', None)
        if leader.squad != squadid:
            return (200, False, 'Squad request outside of your scope ({} =/= {})'.format(leader.squad,squadid), None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)

        members    = session.query(PJ).filter(PJ.squad == leader.squad).all()
        maxmembers = 10
        if len(members) == maxmembers:
            return (200,
                    False,
                    'Squad is already full (slots:{}/{})'.format(len(members),maxmembers),
                    None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(leaderid), None)

    if target:
        if target.squad is not None:
            return (200,
                    False,
                    'PC invited is already in a squad (pcid:{},squadid:{})'.format(target.id,target.squad),
                    None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(targetid), None)

    if target and leader:
        try:
            pc = session.query(PJ).filter(PJ.id == target.id).one_or_none()
            pc.squad      = leader.squad
            pc.squad_rank = 'Pending'
            session.commit()
            members    = session.query(PJ).filter(PJ.squad == leader.squad).all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC Invite failed (slots:{}/{})'.format(len(members),maxmembers),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully invited (slots:{}/{})'.format(len(members),maxmembers),
                    pc)
        finally:
            session.close()
    else:
        return (200,
                False,
                'PC/Leader unknown in DB (leaderid:{},targetid:{})'.format(leaderid,targetid),
                None)

def kick_squad_member(username,leaderid,squadid,targetid):
    (code, success, msg, target) = fn_creature_get(None,targetid)
    (code, success, msg, leader) = fn_creature_get(None,leaderid)
    user                         = fn_user_get(username)
    maxmembers                   = 10
    session                      = Session()

    if leader:
        if leader.squad is None:
            return (200, False, 'PC is not in a squad', None)
        if leader.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope ({} =/= {})'.format(leader.squad,squadid),
                    None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)
        if leader.id == targetid:
            return (200, False, 'PC target cannot be the squad Leader', None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(leaderid), None)

    if target:
        if target.squad is None:
            return (200,
                    False,
                    'PC have to be in a squad (pcid:{},squadid:{})'.format(target.id,target.squad),
                    None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(targetid), None)

    if target and leader:
        try:
            pc = session.query(PJ).filter(PJ.id == target.id).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
            members    = session.query(PJ).filter(PJ.squad == leader.squad).all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC Kick failed (pcid:{},squadid:{})'.format(target.id,target.squad),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully kicked (slots:{}/{})'.format(len(members),maxmembers),
                    None)
        finally:
            session.close()
    else:
        return (200,
                False,
                'PC/Leader unknown in DB (leaderid:{},targetid:{})'.format(leaderid,targetid),
                None)

def accept_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = fn_creature_get(None,pcid)
    user                         = fn_user_get(username)
    session                      = Session()

    if pc:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        if pc.squad_rank != 'Pending':
            return (200, False, 'PC is not pending in a squad', None)

        try:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
            pc.squad_rank = 'Member'
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC squad invite accept failed (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully accepted squad invite (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        finally:
            session.close()
    else: return (200, False, 'PC unknown in DB (pcid:{})'.format(pcid), None)

def decline_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = fn_creature_get(None,pcid)
    user                         = fn_user_get(username)
    session                      = Session()

    if pc:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        if pc.squad_rank != 'Pending':
            return (200, False, 'PC is not pending in a squad', None)

        try:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC squad invite decline failed (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        else:
            return (201, True, 'PC successfully declined squad invite (pcid:{},squadid:{})'.format(pc.id,squadid), None)
        finally:
            session.close()
    else: return (200, False, 'PC unknown in DB (pcid:{})'.format(pcid), None)

def leave_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = fn_creature_get(None,pcid)
    user                         = fn_user_get(username)
    session                      = Session()

    if pc:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        if pc.squad_rank == 'Leader':
            return (200,
                    False,
                    'PC cannot be the squad Leader (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        try:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC squad leave failed (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully left (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        finally:
            session.close()
    else: return (200, False, 'PC unknown in DB (pcid:{})'.format(pcid), None)

#
# Queries /map
#

def get_map(mapid):
    session = Session()

    if mapid:
        try:
            map = session.query(Map).filter(Map.id == mapid).one_or_none()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Map query failed (mapid:{})'.format(mapid), None)
        else:
            if map:
                return (200, True, 'Map query successed (mapid:{})'.format(mapid), map)
            else:
                return (200, False, 'Map does not exist (mapid:{})'.format(mapid), None)
        finally:
            session.close()
    else: return (200, False, 'Incorrect mapid (mapid:{})'.format(mapid), None)

#
# Queries /events
#

def get_mypc_event(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            log   = session.query(Log)\
                           .filter((Log.src == pc.id) | (Log.dst == pc.id))\
                           .order_by(Log.date.desc())\
                           .limit(50)\
                           .all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Event query failed (username:{},pcid:{})'.format(username,pcid),
                    None)
        else:
            return (200, True, 'Events successfully retrieved (pcid:{})'.format(pc.id), log)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)

def get_pc_event(creatureid):
    (code, success, msg, creature) = fn_creature_get(None,creatureid)
    session                        = Session()

    if creature is None: return (200, True, 'Creature does not exist (creatureid:{})'.format(creatureid), None)

    try:
        log   = session.query(Log)\
                       .filter(Log.src == creature.id)\
                       .order_by(Log.date.desc())\
                       .limit(50)\
                       .all()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Event query failed (creatureid:{})'.format(creature.id),
                None)
    else:
        return (200, True, 'Events successfully retrieved (creatureid:{})'.format(creature.id), log)
    finally:
        session.close()

#
# Queries /view
#
def get_view(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            range = 4 + round(pc.p / 50)
            maxx  = pc.x + range
            minx  = pc.x - range
            maxy  = pc.y + range
            miny  = pc.y - range
            view  = session.query(PJ).filter(PJ.instance == pc.instance)\
                                            .filter(PJ.x.between(minx,maxx))\
                                            .filter(PJ.y.between(miny,maxy))\
                                            .all()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] View query failed (username:{},pcid:{}) [{}]'.format(username,pcid,e),
                    None)
        else:
            return (200,
                    True,
                    'View successfully retrieved (range:{},x:{},y:{})'.format(range,pc.x,pc.y),
                    view)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)
