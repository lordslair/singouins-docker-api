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
    if not query_get_pj_exists(pjname,pjid):
        return (404,None)
    else:
        Session = sessionmaker(bind=engine)
        session = Session()

        with engine.connect() as conn:
            if pjid:
                pj = session.query(tables.PJ).filter(tables.PJ.id == pjid).one()
            elif pjname:
                pj = session.query(tables.PJ).filter(tables.PJ.name == pjname).one()
            else: return (422,None)
            session.close()

        if pj: return (200,pj)

def query_get_pjs(username):
    if not query_get_username_exists(username):
        return (404,'This user does not exist')
    else:
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
