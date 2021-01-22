# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import User

def fn_user_get_from_username(username):
    session = Session()

    try:
       user = session.query(User)\
                     .filter(User.name == username)\
                     .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if user: return user
    finally:
        session.close()

def fn_user_get_from_member(member):
    session = Session()
    discordname  = member.name + '#' + member.discriminator

    try:
        user = session.query(User).filter(User.d_name == discordname).one_or_none()
    except Exception as e:
        # Something went wrong during query
        print(e)
        return False
    else:
        if user: return user
    finally:
        session.close()
