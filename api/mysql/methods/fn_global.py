# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Log

#
# LOGGING
#

def clog(src,dst,action):
    session = Session()

    log = Log(src = src, dst = dst, action = action)
    session.add(log)

    try:
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return False
    else:
        return True
    finally:
        session.close()
