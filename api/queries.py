# -*- coding: utf8 -*-

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from datetime  import datetime

from utils     import tables
from variables import SQL_DSN

import textwrap

engine     = create_engine('mysql+pymysql://' + SQL_DSN, pool_recycle=3600)

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
            user = tables.User(name = username,
                               mail = usermail,
                               hash = generate_password_hash(password, rounds = 10),
                               created = datetime.now(),
                               active = True)

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
                return (201, True, 'PC successfully created', None)

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
    (code,pcsrc) = query_get_pc(None,src)
    user         = query_get_user(username)

    Session = sessionmaker(bind=engine)
    session = Session()

    if pcsrc:
        for dst in dsts:
            (code,pcdst) = query_get_pc(None,dst)
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
        return (200, False, 'PC does not exist', None)

def query_get_mp(username,pcid,mpid):
    (code,pc) = query_get_pc(None,pcid)
    user      = query_get_user(username)

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
    (code,pc) = query_get_pc(None,pcid)
    user      = query_get_user(username)

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
    (code,pc) = query_get_pc(None,pcid)
    user      = query_get_user(username)

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

#
# Queries /item
#

def query_get_items(username,pcid):
    (code,pc) = query_get_pc(None,pcid)
    user      = query_get_user(username)

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
