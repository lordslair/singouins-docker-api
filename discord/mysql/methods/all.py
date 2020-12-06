# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

def query_up():
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        try:
            result = session.query(tables.User).first()
        except Exception as e:
            print(e)
        session.close()

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

def query_histo(arg):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        if   arg == 'CreaturesLevel' or arg == 'CL': result = session.query(tables.Creatures.level).all()
        elif arg == 'CreaturesRace'  or arg == 'CR': result = session.query(tables.Creatures.race).all()
        session.close()

    if result: return result
