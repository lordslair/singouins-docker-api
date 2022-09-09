# -*- coding: utf8 -*-

import dataclasses

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import Creature

from nosql.models.RedisStats    import RedisStats


def fn_creature_view_get(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    view_final = []
    try:
        # We check if we have the data in redis
        creature_stats  = RedisStats(creature)._asdict()

        range = 4 + round(creature_stats['base']['p'] / 50)
        maxx  = creature.x + range
        minx  = creature.x - range
        maxy  = creature.y + range
        miny  = creature.y - range

        view  = session.query(Creature)\
                       .filter(Creature.instance == creature.instance)\
                       .filter(Creature.x.between(minx, maxx))\
                       .filter(Creature.y.between(miny, maxy))\
                       .all()

        for creature in view:
            # Lets convert to a dataclass then a dict
            creature       = dataclasses.asdict(creature)
            # We define the default diplomacy title
            creature['diplo'] = 'neutral'
            # We try to define the diplomacy based on tests
            if creature['race'] >= 11:
                creature['diplo'] = 'enemy'

            view_final.append(creature)
    except Exception as e:
        msg = f'{h} View Query KO [{e}]'
        logger.error(msg)
        return None
    else:
        msg = f'{h} View Query OK'
        logger.trace(msg)
        return view_final
    finally:
        session.close()


def fn_creature_squad_view_get(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    # We query the Squad members in the same instance
    try:
        squad = session.query(Creature)\
                       .filter(Creature.instance == creature.instance)\
                       .filter(Creature.squad == creature.squad)\
                       .filter(Creature.squad_rank != 'Pending')\
                       .all()
    except Exception as e:
        msg = f'{h} Squad Query KO (squadid:{creature.squad}) [{e}]'
        logger.error(msg)
        return None
    else:
        if not squad:
            msg = f'{h} Squad Query KO - NotFound (squadid:{creature.squad})'
            logger.warning(msg)
            return None
        else:
            msg = f'{h} Squad Query OK'
            logger.trace(msg)

    views = []       # We initialize the intermadiate array
    view_final = []  # We initialize the result array
    for pc in squad:
        # We check if we have the data in redis
        creature_stats  = RedisStats(pc)._asdict()
        try:
            range = 4 + round(creature_stats['base']['p'] / 50)
            maxx  = pc.x + range
            minx  = pc.x - range
            maxy  = pc.y + range
            miny  = pc.y - range

            view  = session.query(Creature)\
                           .filter(Creature.instance == pc.instance)\
                           .filter(Creature.x.between(minx, maxx))\
                           .filter(Creature.y.between(miny, maxy))\
                           .all()

            if len(views) == 0:
                # We push the first results in the array
                views += view
            else:
                # We aggregate all the results, without duplicates
                views = list(set(views + view))

        except Exception as e:
            msg = f'{h} View Query KO (squadid:{pc.squad}) [{e}]'
            logger.error(msg)
            return None
        else:
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
        finally:
            session.close()

    msg = f'{h} View Query OK (squadid:{pc.squad})'
    logger.trace(msg)
    return view_final
