# -*- coding: utf8 -*-

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from datetime  import datetime

from utils     import tables
from variables import SQL_DSN

engine     = create_engine('mysql+pymysql://' + SQL_DSN, pool_recycle=3600)

#
# Queries: /auth
#

def query_up():
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        try:
            result = session.query(tables.User).first()
            session.close()
        except Exception as e:
            print(e)

    if result: return result

def query_get_user(discordname):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
       result = session.query(tables.User).filter(tables.User.d_name == discordname).one_or_none()
       session.close()

    if result: return result

def query_validate_user(discordname):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        try:
            user = session.query(tables.User).filter(tables.User.d_name == discordname).one_or_none()
            user.d_ack = True
            user.date  = datetime.now()
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return None
