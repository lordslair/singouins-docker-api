# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisStats    import RedisStats

from utils.decorators import (
    check_creature_exists,
    )


def generate_creatures_view(Creature):
    view_final = []
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

    return view_final


def generate_corpses_view(Creature):
    Stats = RedisStats(creatureuuid=Creature.id)
    range = 4 + round(Stats.p / 50)

    maxx  = Creature.x + range
    minx  = Creature.x - range
    maxy  = Creature.y + range
    miny  = Creature.y - range

    CorpsesVisible = RedisSearch().corpse(
        query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
        )

    return CorpsesVisible.results_as_dict


def generate_resources_view(Creature):
    Stats = RedisStats(creatureuuid=Creature.id)
    range = 4 + round(Stats.p / 50)

    maxx  = Creature.x + range
    minx  = Creature.x - range
    maxy  = Creature.y + range
    miny  = Creature.y - range

    ResourcesVisible = RedisSearch().resource(
        query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
        )

    return ResourcesVisible.results_as_dict


#
# Routes /mypc/<uuid:creatureuuid>/view/*
#
# API: GET /mypc/<uuid:creatureuuid>/view
@jwt_required()
# Custom decorators
@check_creature_exists
def view_get(creatureuuid):
    try:
        if g.Creature.squad is None:
            # PC is solo / not in a squad
            try:
                creatures_view = generate_creatures_view(g.Creature)
            except Exception as e:
                msg = f'{g.h} View Query KO [{e}]'
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
                    f"(@squad:{g.Creature.squad.replace('-', ' ')}) & "
                    f"(@squad_rank:-Pending) & "
                    f"(@instance:{g.Creature.instance.replace('-', ' ')})"
                    )
            except Exception as e:
                msg = f'{g.h} Squad Query KO Squad({g.Creature.squad}) [{e}]'
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
                    msg = (f'{g.h} Squad Query KO - NotFound Squad({g.Creature.squad})')
                    logger.warning(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
                else:
                    msg = f'{g.h} Squad Query OK'
                    logger.trace(msg)

            creatures_view = []  # We initialize the result array
            for SquadMember in SquadMembers.results:
                try:
                    view = generate_creatures_view(g.Creature)
                    if len(creatures_view) == 0:
                        # Push the first results in the array
                        creatures_view += view
                    else:
                        # Aggregate without duplicate
                        creatures_view = list(set(creatures_view + view))
                except Exception as e:
                    msg = (f'{g.h} View Query KO Squad({g.Creature.squad}) [{e}]')
                    logger.error(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
    except Exception as e:
        msg = f'{g.h} View Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} View Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": creatures_view,
            }
        ), 200
        """
        When time comes, this should replace the return above:
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creatures": creatures_view,
                    "corpses": generate_corpses_view(g.Creature),
                    "resources": generate_resources_view(g.Creature),
                },
            }
        ), 200
        """
