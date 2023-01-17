# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats    import RedisStats

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{pcid}/view/*
#


# API: GET /mypc/{pcid}/view
@jwt_required()
def view_get(pcid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        if Creature.squad is None:
            # PC is solo / not in a squad
            view_final = []
            try:
                Stats = RedisStats(Creature)
                range = 4 + round(Stats.p / 50)

                maxx  = Creature.x + range
                minx  = Creature.x - range
                maxy  = Creature.y + range
                miny  = Creature.y - range

                Creatures = RedisCreature().search(
                    query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
                    )

                for creature_in_sight in Creatures:
                    # We define the default diplomacy title
                    creature_in_sight['diplo'] = 'neutral'
                    # We try to define the diplomacy based on tests
                    if creature_in_sight['race'] >= 11:
                        creature_in_sight['diplo'] = 'enemy'

                    view_final.append(creature_in_sight)
            except Exception as e:
                msg = f'{h} View Query KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        else:
            # PC is in a squad
            # We query the Squad members in the same instance
            try:
                squad = Creature.squad.replace('-', ' ')
                instance = Creature.instance.replace('-', ' ')
                SquadMembers = RedisCreature().search(
                    f"(@squad:{squad}) & "
                    f"(@squad_rank:-Pending) & "
                    f"(@instance:{instance})"
                    )
            except Exception as e:
                msg = f'{h} Squad Query KO (squadid:{Creature.squad}) [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                if not SquadMembers:
                    msg = (
                        f'{h} Squad Query KO - NotFound '
                        f'(squadid:{Creature.squad})'
                        )
                    logger.warning(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
                else:
                    msg = f'{h} Squad Query OK'
                    logger.trace(msg)

            views = []       # We initialize the intermadiate array
            view_final = []  # We initialize the result array
            for SquadMember in SquadMembers:
                try:
                    CreatureMember = RedisCreature(SquadMember['id'])
                    Stats = RedisStats(CreatureMember)
                    range = 4 + round(Stats.p / 50)

                    maxx  = CreatureMember.x + range
                    minx  = CreatureMember.x - range
                    maxy  = CreatureMember.y + range
                    miny  = CreatureMember.y - range

                    Creatures = RedisCreature().search(
                        query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
                        )

                    if len(views) == 0:
                        # We push the first results in the array
                        views += Creatures
                    else:
                        # We aggregate all the results, without duplicates
                        views = list(set(views + Creatures))

                except Exception as e:
                    msg = f'{h} View Query KO (squadid:{Creature.squad}) [{e}]'
                    logger.error(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
                else:
                    for creature in views:
                        # We define the default diplomacy title
                        creature['diplo'] = 'neutral'
                        # We try to define the diplomacy based on tests
                        if creature['race'] >= 11:
                            creature['diplo'] = 'enemy'
                        if creature['squad'] == Creature.squad:
                            creature['diplo'] = 'squad'

                        view_final.append(creature)
    except Exception as e:
        msg = f'{h} View Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} View Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": view_final,
            }
        ), 200
