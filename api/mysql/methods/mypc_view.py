# -*- coding: utf8 -*-

import dataclasses

from ..session               import Session
from ..models                import Creature

from .fn_creature            import *
from .fn_user                import fn_user_get

from nosql.models.RedisStats import *

#
# Queries /mypc/{pcid}/view/*
#

# API: GET /mypc/<int:pcid>/view
def mypc_view(username,pcid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if user is None:
        return (200,
                False,
                f'User not found (username:{username})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        if pc.squad is None:
            # PC is solo / not in a squad

            # We check if we have the data in redis
            cached_stats = RedisStats(pc).as_dict()
            if cached_stats:
                # Data was in Redis, so we return it
                creature_stats = cached_stats
            else:
                # Data was not in Redis, so we compute it
                generated_stats = RedisStats(pc).refresh().dict
                if generated_stats:
                    # Data was computed, so we return it
                    creature_stats = generated_stats
                else:
                    msg = f'Stats computation KO (pcid:{pc.id})'
                    logger.error(msg)
                    return (200,
                            False,
                            msg,
                            None)

            range = 4 + round(creature_stats['base']['p'] / 50)
            maxx  = pc.x + range
            minx  = pc.x - range
            maxy  = pc.y + range
            miny  = pc.y - range

            view  = session.query(Creature)\
                           .filter(Creature.instance == pc.instance)\
                           .filter(Creature.x.between(minx,maxx))\
                           .filter(Creature.y.between(miny,maxy))\
                           .all()

            view_final = []
            for creature in view:
                # Lets convert to a dataclass then a dict
                creature       = dataclasses.asdict(creature)
                # We define the default diplomacy title
                creature['diplo'] = 'neutral'
                # We try to define the diplomacy based on tests
                if creature['race'] >= 11:
                    creature['diplo'] = 'enemy'

                view_final.append(creature)
        else:
            # PC is in a squad
            # We query the Squad members in the same instance
            squad = session.query(Creature)\
                           .filter(Creature.squad == pc.squad)\
                           .filter(Creature.squad_rank != 'Pending')\
                           .all()
            if not squad:
                return (200,
                        False,
                        f'PC is not in a squad (pcid:{pc.id})',
                        None)

            views = [] # We initialize the result array
            for pc in squad:
                # We check if we have the data in redis
                cached_stats = RedisStats(pc).as_dict()
                if cached_stats:
                    # Data was in Redis, so we return it
                    creature_stats = cached_stats
                else:
                    # Data was not in Redis, so we compute it
                    generated_stats = RedisStats(pc).refresh().dict
                    if generated_stats:
                        # Data was computed, so we return it
                        creature_stats = generated_stats
                    else:
                        msg = f'Stats computation KO (pcid:{pc.id})'
                        logger.error(msg)
                        return (200,
                                False,
                                msg,
                                None)
                try:
                    range = 4 + round(creature_stats['base']['p'] / 50)
                    maxx  = pc.x + range
                    minx  = pc.x - range
                    maxy  = pc.y + range
                    miny  = pc.y - range

                    view  = session.query(Creature)\
                                   .filter(Creature.instance == pc.instance)\
                                   .filter(Creature.x.between(minx,maxx))\
                                   .filter(Creature.y.between(miny,maxy))\
                                   .all()

                    if len(views) == 0:
                        # We push the first results in the array
                        views += view
                    else:
                        # We aggregate all the results, without duplicates
                        views = list(set(views + view))

                except Exception as e:
                    return (200,
                            False,
                            f'[SQL] Squad view query failed (pcid:{pc.id},squadid:{pc.squad}) [{e}]',
                            None)
                else:
                    view_final = []
                    for creature in views:
                        # Lets convert to a dataclass then a dict
                        creature = dataclasses.asdict(creature)
                        # We define the default diplomacy title
                        creature['diplo'] = 'neutral'
                        # We try to define the diplomacy based on tests
                        if creature['race'] >= 11:
                            creature['diplo'] = 'enemy'
                        if creature['squad'] == pc.squad:
                            creature['diplo'] = 'squad'

                        view_final.append(creature)
    except Exception as e:
        return (200,
                False,
                f'[SQL] View query failed (username:{username},pcid:{pcid}) [{e}]',
                None)
    else:
        if view_final:
            return (200,
                    True,
                    f'View query successed (range:{range},x:{pc.x},y:{pc.y})',
                    view_final)
        else:
            return (200,
                    False,
                    f'View query failed (pcid:{pcid})',
                    None)
    finally:
        session.close()
