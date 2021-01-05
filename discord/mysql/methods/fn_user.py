# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import User

def fn_user_get(username):
    session = Session()

    try:
        user = session.query(User).filter(User.name == username).one_or_none()
    except Exception as e:
        # Something went wrong during query
        print(e)
        return False
    else:
        if user: return user
    finally:
        session.close()
