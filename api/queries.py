# -*- coding: utf8 -*-

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from utils     import tables

from datetime  import datetime
from variables import SQL_DSN

engine     = db.create_engine('mysql+pymysql://' + SQL_DSN, pool_recycle=3600)

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
       result = session.query(tables.User).filter(tables.User.name == username).one()
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
            print(user.active)
            user.active = True
            print(user.active)
            session.commit()
        except Exception as e:
            print(e)
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
                print(user.name)
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
t_pjsInfos  = db.Table('pjsInfos', metadata, autoload=True, autoload_with=engine)

def query_get_pj_exists(pjname,pjid):
    if not pjname and not pjid:
        return False
    elif pjname and pjid:
        query = db.select([t_pjsInfos.columns.name]).where(and_(t_pjsInfos.columns.name == pjname,t_pjsInfos.columns.id == pjid))
    elif pjname and not pjid:
        query = db.select([t_pjsInfos.columns.name]).where(t_pjsInfos.columns.name == pjname)
    elif not pjname and pjid:
        query = db.select([t_pjsInfos.columns.id]).where(t_pjsInfos.columns.id == pjid)
    else:
        return False

    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchone()
    if ResultSet:
        return True

def query_new_pj(username,pjname,pjrace):
    if query_get_pj_exists(pjname,None):
        return (409)
    else:
        userid = query_get_pjauth(username)[0]
        query = db.insert(t_pjsInfos).values(name    = pjname,
                                             race    = pjrace,
                                             account = userid,
                                             level   = 1,
                                             x       = 0,
                                             y       = 0,
                                             xp      = 0)
        ResultProxy = connection.execute(query)

        if ResultProxy.inserted_primary_key[0] > 0:
            return (201)

def query_get_pj(pjname,pjid):
    if not query_get_pj_exists(pjname,pjid):
        return (404,None)
    else:
        if pjid:
            query = db.select([t_pjsInfos]).where(t_pjsInfos.columns.id == pjid)
        elif pjname:
            query = db.select([t_pjsInfos]).where(t_pjsInfos.columns.name == pjname)
        else: return (422,None)

        ResultProxy = connection.execute(query)
        ResultSet = ResultProxy.fetchone()
        print(ResultSet)
        if ResultSet:
            return (200,dict(ResultSet))

def query_get_pjs(username):
    if not query_get_user_exists(username):
        return (404,'This user does not exist')
    else:
        userid  = query_get_pjauth(username)[0]
        query = db.select([t_pjsInfos]).where(t_pjsInfos.columns.account == userid)
        ResultProxy = connection.execute(query)
        ResultSet = ResultProxy.fetchall()

        if ResultSet:
            return (200,ResultSet)
        else:
            return (404,'This user has no PJ in DB')

def query_del_pj(username,pjid):
    userid  = query_get_pjauth(username)[0]

    query = db.select([t_pjsInfos.c.id]).where((t_pjsInfos.columns.account == userid) & (t_pjsInfos.columns.id == pjid))
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchone()

    if ResultSet:
        if ResultSet[0] == pjid: # The pjid requested to DELETE belongs to the token user
            query = db.delete(t_pjsInfos).where(t_pjsInfos.c.id == pjid)
            ResultProxy = connection.execute(query)
            if ResultProxy.rowcount == 1:
                return (200)
        else:
            return (400)
    else:
        return (404)
