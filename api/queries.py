# -*- coding: utf8 -*-

import sqlalchemy as db

from datetime  import datetime
from variables import SQL_DSN

engine     = db.create_engine('mysql+pymysql://' + SQL_DSN)
connection = engine.connect()
metadata   = db.MetaData()
t_pjsAuth  = db.Table('pjsAuth', metadata, autoload=True, autoload_with=engine)

def query_get_user_exists(username):
    query = db.select([t_pjsAuth.columns.name]).where(t_pjsAuth.columns.name == username)
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchone()
    if ResultSet:
        return True

def query_get_password(username):
    query = db.select([t_pjsAuth.columns.hash]).where(t_pjsAuth.columns.name == username)
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchone()
    if ResultSet:
        return ResultSet[0]

def query_set_pjauth(username,password,usermail):
    if query_get_user_exists(username):
        return (409)
    else:
        query = db.insert(t_pjsAuth).values(name    = username,
                                            hash    = password,
                                            mail    = usermail,
                                            created = datetime.now(),
                                            active  = True)
        ResultProxy = connection.execute(query)

        if ResultProxy.inserted_primary_key[0] > 0:
            return (201)
