# -*- coding: utf8 -*-

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from utils     import tables

from datetime  import datetime
from variables import SQL_DSN

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
# Queries: /pj
#

def query_get_pj_exists(pjname,pjid):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if not pjname and not pjid:
            return False
        elif pjname and pjid:
            result = session.query(tables.PJ).filter(tables.PJ.name == pjname, tables.PJ.id == pjid).one_or_none()
        elif pjname and not pjid:
            result = session.query(tables.PJ).filter(tables.PJ.name == pjname).one_or_none()
        elif not pjname and pjid:
            result = session.query(tables.PJ).filter(tables.PJ.id == pjid).one_or_none()
        else:
            return False

    if result: return True

def query_add_pj(username,pjname,pjrace):
    if query_get_pj_exists(pjname,None):
        return (409)
    else:
        Session = sessionmaker(bind=engine)
        session = Session()
        with engine.connect() as conn:
            pj = tables.PJ(name    = pjname,
                           race    = pjrace,
                           account = query_get_user(username).id,
                           level   = 1,
                           x       = 0,
                           y       = 0,
                           xp      = 0)

            session.add(pj)

            try:
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (422)
            else:
                return (201)

def query_get_pj(pjname,pjid):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if pjid:
            pj = session.query(tables.PJ).filter(tables.PJ.id == pjid).one_or_none()
        elif pjname:
            pj = session.query(tables.PJ).filter(tables.PJ.name == pjname).one_or_none()
        else: return (422,None)
        session.close()

    if pj:
        return (200,pj)
    else:
        return (404,'This PJ does not exist')

def query_get_pjs(username):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        userid = query_get_user(username).id
        pjs    = session.query(tables.PJ).filter(tables.PJ.account == userid).all()
        session.close()

    if pjs:
        return (200,pjs)
    else:
        return (404,'This user has no PJ in DB')

def query_del_pj(username,pjid):

    if not query_get_pj_exists(None,pjid):
        return (404)
    else:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            try:
                userid  = query_get_user(username).id
                pj = session.query(tables.PJ).filter(tables.PJ.account == userid, tables.PJ.id == pjid).one_or_none()
                session.delete(pj)
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (422)
            else:
                return (200)

#
# Queries: /mp
#

def query_add_mp(username,src,dsts,subject,body):
    (code,pjsrc) = query_get_pj(None,src)
    user         = query_get_user(username)

    Session = sessionmaker(bind=engine)
    session = Session()

    if pjsrc:
        for dst in dsts:
            (code,pjdst) = query_get_pj(None,dst)
            if pjdst:
                with engine.connect() as conn:
                    mp = tables.MP(src_id  = pjsrc.id,
                                   src     = pjsrc.name,
                                   dst_id  = pjdst.id,
                                   dst     = pjdst.name,
                                   subject = subject,
                                   body    = body)
                    session.add(mp)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (422, {"msg": "MP creation failed"})
        else:
            return (201, {"msg": "MP successfully created"})

    elif user.id != pjsrc.account:
        return (409, {"msg": "Token/username mismatch"})
    else:
        return (404, {"msg": "PJ does not exist"})

def query_get_mp(username,pjid,mpid):
    (code,pj) = query_get_pj(None,pjid)
    user      = query_get_user(username)

    if pj and pj.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            mp = session.query(tables.MP).filter(tables.MP.dst_id == pj.id, tables.MP.id == mpid).one_or_none()
            session.close()

        if mp:
            return (200, mp)
        else:
            return (404, {"msg": "No MP found for this PJ"})
    else: return (409, {"msg": "Token/username mismatch"})

def query_del_mp(username,pjid,mpid):
    (code,pj) = query_get_pj(None,pjid)
    user      = query_get_user(username)

    if pj and pj.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            try:
                mp = session.query(tables.MP).filter(tables.MP.dst_id == pj.id, tables.MP.id == mpid).one_or_none()
                if not mp: return (404, {"msg": "No MP found for this PJ"})
                session.delete(mp)
                session.commit()
            except Exception as e:
                # Something went wrong during commit
                return (422, {"msg": "MP deletion failed"})
            else:
                return (200, {"msg": "MP successfully deleted"})
    else: return (409, {"msg": "Token/username mismatch"})

def query_get_mps(username,pjid):
    (code,pj) = query_get_pj(None,pjid)
    user      = query_get_user(username)

    if pj and pj.account == user.id:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            mps = session.query(tables.MP.id,
                                tables.MP.date,
                                tables.MP.dst,
                                tables.MP.dst_id,
                                tables.MP.subject,
                                tables.MP.src,
                                tables.MP.src_id).filter(tables.MP.dst_id == pj.id).all()

        if mps:
            return (200, mps)
        else:
            return (404, {"msg": "No MP found for this PJ"})
    else: return (409, {"msg": "Token/username mismatch"})
