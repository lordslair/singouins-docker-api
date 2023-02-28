# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisStats    import RedisStats

from utils.routehelper          import (
    creature_check,
    )


#
# Routes /mypc/<uuid:creatureuuid>/view/*
#
# API: GET /mypc/<uuid:creatureuuid>/view
@jwt_required()
def view_get(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        if Creature.squad is None:
            # PC is solo / not in a squad
            view_final = []
            try:
                Stats = RedisStats(creatureuuid=Creature.id)
                range = 4 + round(Stats.p / 50)

                maxx  = Creature.x + range
                minx  = Creature.x - range
                maxy  = Creature.y + range
                miny  = Creature.y - range

                CreaturesVisible = RedisSearch().creature(
                    query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
                    )

                for CreatureVisible in CreaturesVisible.results:
                    creature_in_sight = CreatureVisible.as_dict()
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
                SquadMembers = RedisSearch().creature(
                    f"(@squad:{Creature.squad.replace('-', ' ')}) & "
                    f"(@squad_rank:-Pending) & "
                    f"(@instance:{Creature.instance.replace('-', ' ')})"
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
                if not SquadMembers or len(SquadMembers.results) == 0:
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
            for SquadMember in SquadMembers.results:
                try:
                    Stats = RedisStats(creatureuuid=SquadMember.id)
                    range = 4 + round(Stats.p / 50)

                    maxx  = SquadMember.x + range
                    minx  = SquadMember.x - range
                    maxy  = SquadMember.y + range
                    miny  = SquadMember.y - range

                    CreaturesVisible = RedisSearch().creature(
                        query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
                        )

                    if len(views) == 0:
                        # We push the first results in the array
                        views += CreaturesVisible.results
                    else:
                        # We aggregate all the results, without duplicates
                        views = list(set(views + CreaturesVisible.results))

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
                    for CreatureVisible in views:
                        creature_in_sight = CreatureVisible.as_dict()
                        # We define the default diplomacy title
                        creature_in_sight['diplo'] = 'neutral'
                        # We try to define the diplomacy based on tests
                        if creature_in_sight['race'] >= 11:
                            creature_in_sight['diplo'] = 'enemy'
                        if creature_in_sight['squad'] == Creature.squad:
                            creature_in_sight['diplo'] = 'squad'

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
        msg = f'{h} View Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": view_final,
            }
        ), 200
