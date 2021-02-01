# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

def query_user_validate(usermail, discordname):
    session = Session()

    try:
        user = session.query(User)\
                      .filter(User.mail == usermail)\
                      .one_or_none()

        user.d_name    = discordname
        user.d_ack     = True
        user.date      = datetime.now()
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        print(e)
        return False
    else:
        if user:
            return user
    finally:
        session.close()
