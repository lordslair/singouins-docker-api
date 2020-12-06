# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

def query_up():
    session = Session()

    try:
        result = session.query(User).first()
    except Exception as e:
        print(e)
    else:
        if result: return result
    finally:
        session.close()

def query_get_user(discordname):
    session = Session()

    result = session.query(User).filter(User.d_name == discordname).one_or_none()
    session.close()

    if result: return result

def query_validate_user(discordname):
    session = Session()

    try:
        user = session.query(User).filter(User.d_name == discordname).one_or_none()
        user.d_ack = True
        user.date  = datetime.now()
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return None

def query_histo(arg):
    session = Session()

    if   arg == 'CreaturesLevel' or arg == 'CL': result = session.query(Creature.level).all()
    elif arg == 'CreaturesRace'  or arg == 'CR': result = session.query(Creature.race).all()
    session.close()

    if result: return result
