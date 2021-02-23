# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get

#
# Queries /mypc/<int:pcid>/squad/<int:squadid>/view/*
#

# API: /mypc/<int:pcid>/squad/<int:squadid>/view
def mysquad_view_get(username,pcid,squadid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    f'Squad request outside of your scope (pcid:{pcid},squadid:{squadid})',
                    None)

        try:
            squad = session.query(PJ).\
                            filter(PJ.squad == pc.squad).\
                            filter(PJ.squad_rank != 'Pending').all()

        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    f'[SQL] Squad query failed (pcid:{pcid},squadid:{squadid})',
                    None)
        else:
            if not squad:
                return (200,
                        False,
                        f'PC is not in a squad (pcid:{pcid},squadid:{squadid})',
                        None)

            views = [] # We initialize the result array
            for pc in squad:
                try:
                    range = 4 + round(pc.p / 50)
                    maxx  = pc.x + range
                    minx  = pc.x - range
                    maxy  = pc.y + range
                    miny  = pc.y - range

                    view  = session.query(PJ).filter(PJ.instance == pc.instance)\
                                             .filter(PJ.x.between(minx,maxx))\
                                             .filter(PJ.y.between(miny,maxy)).all()
                    if len(views) == 0:
                        # We push the first results in the array
                        views += view
                    else:
                        # We aggregate all the results, without  duplicates
                        views = list(set(views + view))

                except Exception as e:
                    return (200,
                            False,
                            f'[SQL] Squad view query failed (pcid:{pcid},squadid:{squadid})',
                            None)
                else:
                    return (200,
                            True,
                            f'Squad view query successed (pcid:{pcid},squadid:{squadid})',
                            views)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)
