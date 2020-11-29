# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *

def fn_user_get(username):
    session = Session()

    try:
       result = session.query(User)\
                       .filter(User.name == username)\
                       .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return result
    finally:
        session.close()
