# -*- coding: utf8 -*-

import dataclasses

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
            # We create the empty list for the payload
            creatures = []
            # We loop over all the creatures in the view
            for elem in view:
                # We transform elem into a dict through the dataclass
                creature = dataclasses.asdict(elem)

                # We define the default diplomacy title
                creature['diplo'] = 'neutral'

                # We try to define the diplomacy based on tests
                if creature['race'] > 11:
                    creature['diplo'] = 'enemy'
                if creature['squad'] == pc.squad:
                    creature['diplo'] = 'squad'
                else:
                    pass

                # We remove MRVGPB caracs from view
                if creature['m']: del creature['m']
                if creature['r']: del creature['r']
                if creature['v']: del creature['v']
                if creature['g']: del creature['g']
                if creature['p']: del creature['p']
                if creature['b']: del creature['b']
                # We remove HP, ARM, and XP too
                if creature['hp']: del creature['hp']
                if creature['hp_max']: del creature['hp_max']
                if creature['arm_b']: del creature['arm_b']
                if creature['arm_p']: del creature['arm_p']
                if creature['xp']: del creature['xp']

                # We re-inject the creature into the final list
                creatures.append(creature)
            return (200,
                    True,
                    'View successfully retrieved (range:{},x:{},y:{})'.format(range,pc.x,pc.y),
                    creatures)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)
