# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

from .fn_user           import *

def query_user_validate(username,discordname):
    session = Session()
    user    = fn_user_get(username)

    # Check if the user is already validated by someone else
    if user.d_name is not None or user.d_name != discordname:
        return False

    try:
        user.d_name = discordname
        user.date   = datetime.now()
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        print(e)
        return False
    else:
        if user: return user
    finally:
        session.close()
