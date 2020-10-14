# -*- coding: utf8 -*-

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from datetime  import datetime
from random    import randint

from utils     import tables
from variables import SQL_DSN

import textwrap

engine     = create_engine('mysql+pymysql://' + SQL_DSN, pool_recycle=3600)

#
# LOGGING
#

def clog(src,dst,action):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        log = tables.Log(src    = src,
                         dst    = dst,
                         action = action)

        session.add(log)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return False
        else:
            return True

#
# Queries: /auth
#

def query_get_username_exists(username):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        result = session.query(tables.User).filter(tables.User.name == username).one_or_none()
        session.close()

    if result: return True

def query_get_usermail_exists(usermail):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
       result = session.query(tables.User).filter(tables.User.mail == usermail).one_or_none()
       session.close()

    if result: return True

def query_get_user(username):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
       result = session.query(tables.User).filter(tables.User.name == username).one_or_none()
       session.close()

    if result: return result

def query_add_user(username,password,usermail):
    if query_get_username_exists(username) or query_get_usermail_exists(usermail):
        return (409)
    else:
        from flask_bcrypt import generate_password_hash

        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            user = tables.User(name      = username,
                               mail      = usermail,
                               hash      = generate_password_hash(password, rounds = 10),
                               d_name    = '',
                               d_monkeys = '', # Todo later
                               d_ack     = False,
                               created   = datetime.now(),
                               active    = True)

            session.add(user)

            try:
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (422)
            else:
                return (201)

def query_set_user_confirmed(usermail):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        try:
            user = session.query(tables.User).filter(tables.User.mail == usermail).one_or_none()
            user.active = True
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (422)
        else:
            return (201)

def query_del_user(username):
    if not query_get_username_exists(username):
        return (404)
    else:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            try:
                user = session.query(tables.User).filter(tables.User.name == username).one_or_none()
                session.delete(user)
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (422)
            else:
                return (200)

#
# Queries: /pc
#

def query_get_pc_exists(pcname,pcid):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if not pcname and not pcid:
            return False
        elif pcname and pcid:
            result = session.query(tables.PJ).filter(tables.PJ.name == pcname, tables.PJ.id == pcid).one_or_none()
        elif pcname and not pcid:
            result = session.query(tables.PJ).filter(tables.PJ.name == pcname).one_or_none()
        elif not pcname and pcid:
            result = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
        else:
            return False

    if result: return True

def query_add_pc(username,pcname,pcrace):
    if query_get_pc_exists(pcname,None):
        return (409, False, 'PC already exists', None)
    else:
        Session = sessionmaker(bind=engine)
        session = Session()
        with engine.connect() as conn:
            pc = tables.PJ(name    = pcname,
                           race    = pcrace,
                           account = query_get_user(username).id,
                           level   = 1,
                           x       = 0,
                           y       = 0,
                           xp      = 0)

            session.add(pc)

            try:
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC creation failed', None)
            else:
                return (201, True, 'PC successfully created', pc)

def query_get_pc(pcname,pcid):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if pcid:
            pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
        elif pcname:
            pc = session.query(tables.PJ).filter(tables.PJ.name == pcname).one_or_none()
        else: return (200, False, 'Wrong pcid/pcname', None)
        session.close()

    if pc:
        return (200, True, 'OK', pc)
    else:
        return (200, False, 'PC does not exist', None)

def query_get_pcs(username):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        userid = query_get_user(username).id
        pcs    = session.query(tables.PJ).filter(tables.PJ.account == userid).all()
        session.close()

    if pcs:
            return (200, True, 'OK', pcs)
    else:
        return (200, False, 'No PC found for this user', None)

def query_del_pc(username,pcid):

    if not query_get_pc_exists(None,pcid):
        return (200, False, 'PC does not exist', None)
    else:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            try:
                userid  = query_get_user(username).id
                pc = session.query(tables.PJ).filter(tables.PJ.account == userid, tables.PJ.id == pcid).one_or_none()
                session.delete(pc)
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC deletion failed', None)
            else:
                return (200, True, 'PC successfully deleted', None)

#
# Queries: /mp
#

def query_add_mp(username,src,dsts,subject,body):
    (code, success, msg, pcsrc) = query_get_pc(None,src)
    user                        = query_get_user(username)

    Session = sessionmaker(bind=engine)
    session = Session()

    if pcsrc:
        for dst in dsts:
            (code, success, msg, pcdst) = query_get_pc(None,dst)
            if pcdst:
                with engine.connect() as conn:
                    mp = tables.MP(src_id  = pcsrc.id,
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
            return (200, False, 'MP creation failed', None)
        else:
            return (201, True, 'MP successfully created', None)

    elif user.id != pcsrc.account:
        return (409, False, 'Token/username mismatch', None)
    else:
        return (200, False, 'PC does not exist', mp)

def query_get_mp(username,pcid,mpid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            mp = session.query(tables.MP).filter(tables.MP.dst_id == pc.id, tables.MP.id == mpid).one_or_none()
            session.close()

        if mp:
            return (200, True, 'OK', mp)
        else:
            return (200, True, 'No MP found for this PC', None)
    else: return (409, False, 'Token/username mismatch', None)

def query_del_mp(username,pcid,mpid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            try:
                mp = session.query(tables.MP).filter(tables.MP.dst_id == pc.id, tables.MP.id == mpid).one_or_none()
                if not mp: return (200, True, 'No MP found for this PC', None)
                session.delete(mp)
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'MP deletion failed', None)
            else:
                return (200, True, 'MP successfully deleted', None)
    else: return (409, False, 'Token/username mismatch', None)

def query_get_mps(username,pcid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            mps = session.query(tables.MP).filter(tables.MP.dst_id == pc.id).all()

        if mps:
            for mp in mps:
                mp.body = textwrap.shorten(mp.body, width=50, placeholder="...")
            return (200, True, 'OK', mps)
        else:
            return (200, True, 'No MP found for this PC', None)
    else: return (409, False, 'Token/username mismatch', None)

def query_get_mp_addressbook(username,pcid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            addressbook = session.query(tables.PJ).with_entities(tables.PJ.id,tables.PJ.name).all()

        if addressbook:
            return (200, True, 'OK', addressbook)
        else:
            return (200, True, 'No Addressbook found for this PC', None)
    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /item
#

def query_get_items(username,pcid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            weapons = session.query(tables.Weapons).filter(tables.Weapons.bearer == pc.id).all()
            gear    = session.query(tables.Gear).filter(tables.Gear.bearer == pc.id).all()
            return (200, True, 'OK', {"weapons": weapons, "gear": gear})

    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /meta
#

def query_get_meta_item(itemtype):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if    itemtype == 'weapon': meta = session.query(tables.WeaponsMeta).all()
        elif  itemtype == 'gear':   meta = session.query(tables.GearMeta).all()
        else: return (200, False, 'Itemtype does not exist', None)

    if meta:
        return (200, True, 'OK', meta)

#
# Queries /squad
#

def query_get_squad(username,pcid,squadid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            squad = session.query(tables.Squad).\
                            filter(tables.Squad.id == pc.squad).\
                            filter(tables.PJ.id == pc.id)

            if squad.filter(tables.PJ.squad_rank != 'Pending').one_or_none():
                squad   = squad.session.query(tables.Squad).filter(tables.Squad.id == pc.squad).one_or_none()
                members = session.query(tables.PJ).filter(tables.PJ.squad == squad.id).filter(tables.PJ.squad_rank != 'Pending').all()
                pending = session.query(tables.PJ).filter(tables.PJ.squad == squad.id).filter(tables.PJ.squad_rank == 'Pending').all()
                if squad:
                    if isinstance(members, list):
                        if isinstance(pending, list):
                            return (200, True, 'OK', {"squad": squad, "members": members, "pending": pending})
                        else: return (200, False, 'SQL Error retrieving pending PC in squad', None)
                    else: return (200, False, 'SQL Error retrieving members PC in squad', None)
                else: return (200, False, 'SQL Error retrieving squad', None)

            elif squad.filter(tables.PJ.squad_rank == 'Pending').one_or_none():
                squad   = squad.session.query(tables.Squad).filter(tables.Squad.id == pc.squad).one_or_none()
                return (200, True, 'PC is pending in a squad', {"squad": squad})
            else: return (200, False, 'PC is not in a squad', None)
    else: return (409, False, 'Token/username mismatch', None)

def query_add_squad(username,pcid,squadname):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            if session.query(tables.Squad).filter(tables.Squad.name == squadname).one_or_none():
                return (409, False, 'Squad already exists', None)
            if pc.squad is not None:
                return (200, False, 'Squad leader already in a squad', None)

            squad = tables.Squad(name    = squadname,
                                 leader  = pc.id,
                                 created = datetime.now())
            session.add(squad)

            try:
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'Squad creation failed', None)
            else:
                # Squad created, let's assign the team creator in the squad
                try:
                    pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                    pc.squad      = squad.id
                    pc.squad_rank = 'Leader'
                    session.commit()
                except Exception as e:
                    # Something went wrong during commit
                    return (200, False, 'Squad leader assignation failed', None)
                else:
                    return (201, True, 'Squad successfully created', squad)
    else: return (409, False, 'Token/username mismatch', None)

def query_del_squad(username,pcid,squadid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            try:
                squad = session.query(tables.Squad).filter(tables.Squad.leader == pc.id).one_or_none()
                if not squad: return (200, True, 'No Squad found for this PC', None)

                count = session.query(tables.PJ).filter(tables.PJ.squad == squad.id).count()
                if count > 1: return (200, False, 'Squad not empty', None)

                session.delete(squad)
                pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                pc.squad      = None
                pc.squad_rank = None
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'Squad deletion failed', None)
            else:
                return (200, True, 'Squad successfully deleted', None)
    else: return (409, False, 'Token/username mismatch', None)

def query_invite_squad_member(username,leaderid,pcid,squadid):
    (code, success, msg, pc)     = query_get_pc(None,pcid)
    (code, success, msg, leader) = query_get_pc(None,leaderid)
    user                         = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc and leader:
        Session = sessionmaker(bind=engine)
        session = Session()

        if leader.squad is None:
            return (200, False, 'PC is not in a squad', None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)
        if pc.squad is not None:
            return (200, False, 'PC invited is already in a squad', None)

        with engine.connect() as conn:
            try:
                pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                pc.squad      = leader.squad
                pc.squad_rank = 'Pending'
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC Invite failed', None)
            else:
                return (201, True, 'PC successfully invited', pc)
    else: return (200, False, 'PC unknown in DB', None)

def query_kick_squad_member(username,leaderid,pcid,squadid):
    (code, success, msg, pc)     = query_get_pc(None,pcid)
    (code, success, msg, leader) = query_get_pc(None,leaderid)
    user                         = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc and leader:
        Session = sessionmaker(bind=engine)
        session = Session()

        if leader.squad is None:
            return (200, False, 'PC is not in a squad', None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)
        if pc.squad is None:
            return (200, False, 'PC target is not in a squad', None)
        if pc.id == leader.id:
            return (200, False, 'PC target cannot be the squad Leader', None)

        with engine.connect() as conn:
            try:
                pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                pc.squad      = None
                pc.squad_rank = None
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC Kick failed', None)
            else:
                return (201, True, 'PC successfully kicked', None)
    else: return (200, False, 'PC/Leader unknown in DB', None)

def query_accept_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = query_get_pc(None,pcid)
    user                         = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc:
        Session = sessionmaker(bind=engine)
        session = Session()

        if pc.squad_rank != 'Pending':
            return (200, False, 'PC is not pending in a squad', None)

        with engine.connect() as conn:
            try:
                pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                pc.squad_rank = 'Member'
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC squad invite accept failed', None)
            else:
                return (201, True, 'PC successfully accepted', None)
    else: return (200, False, 'PC unknown in DB', None)

def query_decline_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = query_get_pc(None,pcid)
    user                         = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc:
        Session = sessionmaker(bind=engine)
        session = Session()

        if pc.squad_rank != 'Pending':
            return (200, False, 'PC is not pending in a squad', None)

        with engine.connect() as conn:
            try:
                pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                pc.squad      = None
                pc.squad_rank = None
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC squad invite decline failed', None)
            else:
                return (201, True, 'PC successfully declined squad invite', None)
    else: return (200, False, 'PC unknown in DB', None)

def query_leave_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = query_get_pc(None,pcid)
    user                         = query_get_user(username)

    if pc.squad != squadid: return (200, False, 'Squad request outside of your scope', None)
    if pc:
        Session = sessionmaker(bind=engine)
        session = Session()

        if pc.squad_rank == 'Leader':
            return (200, False, 'PC cannot be the squad Leader', None)

        with engine.connect() as conn:
            try:
                pc = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                pc.squad      = None
                pc.squad_rank = None
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (200, False, 'PC squad leave failed', None)
            else:
                return (201, True, 'PC successfully left', None)
    else: return (200, False, 'PC unknown in DB', None)

#
# Queries /map
#

def query_get_map(mapid):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if mapid:
            map = session.query(tables.Map).filter(tables.Map.id == mapid).one_or_none()
        else: return (200, False, 'Wrong mapid', None)
        session.close()

    if map:
        return (200, True, 'OK', map)
    else:
        return (200, False, 'Map does not exist', None)

#
# Queries /events
#

def query_event(username,pcid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            log   = session.query(tables.Log).filter((tables.Log.src == pcid) | (tables.Log.dst == pcid)).limit(50).all()
            return (200, True, 'Logs successfully retrieved', log)
    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /action
#

def query_move_path(username,pcid,path):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        from rqueries import rget_pa,rset_pa

        for coords in path:
            (code, success, msg, pc) = query_get_pc(None,pcid)
            bluepa                   = rget_pa(pcid)[3]['blue']['pa']
            x,y                      = map(int, coords.strip('()').split(','))

            if abs(pc.x - x) <= 1 and abs(pc.y - y) <= 1:
                if bluepa > 1:
                    # Enough PA to move
                    rset_pa(pcid,0,1) # We consume the blue PA (1) right now
                    Session = sessionmaker(bind=engine)
                    session = Session()

                    with engine.connect() as conn:
                        try:
                            pc   = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
                            oldx = pc.x
                            oldy = pc.y
                            pc.x = x
                            pc.y = y
                            session.commit()
                        except Exception as e:
                            # Something went wrong during commit
                            return (200, False, 'Coords update failed', None)
                        else:
                            clog(pc.id,None,'Moved from ({},{}) to ({},{})'.format(oldx,oldy,pc.x,pc.y))
                else:
                    # Not enough PA to move
                    return (200, False, 'Not enough PA to move', None)
            else:
                return (200, False, 'Coords incorrect', path)
        return (200, True, 'PC successfully moved', rget_pa(pcid)[3])
    else: return (409, False, 'Token/username mismatch', None)

def query_action_attack(username,pcid,weaponid,targetid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        from rqueries import rget_pa,rset_pa

        if weaponid == 0:
            (code, success, msg, tg) = query_get_pc(None,targetid)
            redpa                    = rget_pa(pcid)[3]['red']['pa']
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
                            if randint(1, 100) <= 5:
                                # The attack is a critical Hit
                                dmg_crit = round(150 + pc.r / 10)
                                clog(pc.id,tg.id,'Critically Attacked {}'.format(tg.name))
                                clog(tg.id,pc.id,'Critically Hit by {}'.format(pc.name))
                            else:
                                # The attack is a normal Hit
                                dmg_crit = 100
                                clog(pc.id,tg.id,'Attacked {}'.format(tg.name))
                                clog(tg.id,pc.id,'Hit by {}'.format(pc.name))
                            dmg = round(dmg_wp * dmg_crit / 100) - tg.arm_p
                            if dmg > 0:
                                # The attack deals damage
                                action['damages'] = dmg
                                hp = tg.hp - dmg

                                if hp >= 0:
                                    # The attack wounds
                                    Session = sessionmaker(bind=engine)
                                    session = Session()

                                    with engine.connect() as conn:
                                        try:
                                            tg    = session.query(tables.PJ).filter(tables.PJ.id == targetid).one_or_none()
                                            tg.hp = hp
                                            session.commit()
                                        except Exception as e:
                                            # Something went wrong during commit
                                            return (200, False, 'HP update failed', None)
                                        else:
                                            clog(pc.id,None,'Suffered minor injuries ({})'.format(dmg))
                                else:
                                    # The attack kills
                                    action['killed'] = True
                                    clog(pc.id,tg.id,'Killed {}'.format(tg.name))
                                    clog(tg.id,pc.id,'Died'.format(pc.name))
                            else:
                                clog(pc.id,None,'Suffered no injuries')
                                # The attack does not deal damage
                        else:
                            # The attack missed
                            clog(pc.id,tg.id,'Missed {}'.format(tg.name))
                            clog(tg.id,pc.id,'Avoided {}'.format(pc.name))
                    else:
                        # Failed action
                        clog(pc.id,None,'Failed an attack')
                else:
                    # Not enough PA to attack
                    return (200, False, 'Not enough PA to attack', None)
            else:
                # Target is too far
                return (200, False, 'Coords incorrect', None)
        return (200, True, 'Target successfully attacked', {"red": rget_pa(pcid)[3]['red'],
                                                            "blue": rget_pa(pcid)[3]['blue'],
                                                            "action": action})
    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /view
#
def query_get_view(username,pcid):
    (code, success, msg, pc) = query_get_pc(None,pcid)
    user                     = query_get_user(username)

    if pc and pc.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            view = session.query(tables.PJ).filter(tables.PJ.instance == pc.instance).all()
            return (200, True, 'View successfully retrieved', view)

    else: return (409, False, 'Token/username mismatch', None)
