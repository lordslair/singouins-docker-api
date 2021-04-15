# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *

from .fn_creature       import fn_creature_get, fn_creatures_clean
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
            return (200,
                    False,
                    f'[SQL] View query failed (username:{username},pcid:{pcid}) [{e}]',
                    None)
        else:
            # We clean the creatures in view, and get a list
            creatures = fn_creatures_clean(view)
            for creature in creatures:
                # We define the default diplomacy title
                creature['diplo'] = 'neutral'
                # We try to define the diplomacy based on tests
                if creature['race'] > 11:
                    creature['diplo'] = 'enemy'
                if creature['squad'] == pc.squad:
                    creature['diplo'] = 'squad'
                else:
                    pass

            return (200,
                    True,
                    f'View successfully retrieved (range:{range},x:{x},y:{y})',
                    creatures)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)
