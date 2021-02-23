# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get

#
# Queries /mypc/{pcid}/view/*
#

# API: /mypc/<int:pcid>/view
def mypc_view_get(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            range = 4 + round(pc.p / 50)
            maxx  = pc.x + range
            minx  = pc.x - range
            maxy  = pc.y + range
            miny  = pc.y - range
            view  = session.query(PJ).filter(PJ.instance == pc.instance)\
                                            .filter(PJ.x.between(minx,maxx))\
                                            .filter(PJ.y.between(miny,maxy))\
                                            .all()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] View query failed (username:{},pcid:{}) [{}]'.format(username,pcid,e),
                    None)
        else:
            return (200,
                    True,
                    'View successfully retrieved (range:{},x:{},y:{})'.format(range,pc.x,pc.y),
                    view)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)
