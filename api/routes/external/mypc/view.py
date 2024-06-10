# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger
from mongoengine import Q

from nosql.models.RedisSearch   import RedisSearch

from mongo.models.Creature import CreatureDocument
from mongo.models.Squad import SquadDocument

from utils.decorators import (
    check_creature_exists,
    )


def generate_creatures_view(Creature):
    creatures_view = []

    if Creature.x is None or Creature.y is None:
        return creatures_view

    range = 4 + round(Creature.stats.total.p / 50)

    maxx  = Creature.x + range
    minx  = Creature.x - range
    maxy  = Creature.y + range
    miny  = Creature.y - range

    query = (
        Q(x__gte=minx) & Q(x__lte=maxx)
        & Q(y__gte=miny) & Q(y__lte=maxy)
        )
    CreaturesVisible = CreatureDocument.objects.filter(query)

    for CreatureVisible in CreaturesVisible:
        creature_in_sight = CreatureVisible.to_json()
        # We define the default diplomacy title
        creature_in_sight['diplo'] = 'neutral'
        # We try to define the diplomacy based on tests
        if creature_in_sight['race'] >= 11:
            creature_in_sight['diplo'] = 'enemy'

        creatures_view.append(creature_in_sight)

    return creatures_view


def generate_corpses_view(Creature):
    corpses_view = []

    if Creature.x is None or Creature.y is None:
        return corpses_view

    range = 4 + round(g.Creature.stats.total.p / 50)

    maxx  = Creature.x + range
    minx  = Creature.x - range
    maxy  = Creature.y + range
    miny  = Creature.y - range

    CorpsesVisible = RedisSearch().corpse(
        query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
        )

    return CorpsesVisible.results_as_dict


def generate_resources_view(Creature):
    resources_view = []

    if Creature.x is None or Creature.y is None:
        return resources_view

    range = 4 + round(g.Creature.stats.total.p / 50)

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

    if hasattr(g.Creature.squad, 'instance') is False:
        msg = f'{g.h} View Query OK (WORLDMAP)'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creatures": [],
                    "corpses": [],
                    "resources": [],
                },
            }
        ), 200

    if hasattr(g.Creature.squad, 'id'):
        # Creature in a squad
        try:
            query = (
                Q(squad__id=g.Creature.squad.id) &
                Q(instance=g.Creature.instance) &
                Q(squad__rank__ne="Pending")
                )
            SquadMembers = SquadDocument.objects.filter(query)
        except Exception as e:
            msg = f'{g.h} Squad({g.Creature.squad.id}) Query KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            if not SquadMembers or SquadMembers.count() == 0:
                msg = (f'{g.h} Squad({g.Creature.squad.id}) Query KO - NotFound')
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                msg = f'{g.h} Squad({g.Creature.squad}) Query OK'
                logger.trace(msg)

        creatures_view = []  # We initialize the result array
        for SquadMember in SquadMembers.all():
            try:
                view = generate_creatures_view(g.Creature)
                if len(creatures_view) == 0:
                    # Push the first results in the array
                    creatures_view += view
                else:
                    # Aggregate without duplicate
                    creatures_view = list(set(creatures_view + view))
            except Exception as e:
                msg = (f'{g.h} Squad({g.Creature.squad}) View Query KO [{e}]')
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
    else:
        # Creature not in a squad
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

    msg = f'{g.h} View Query OK'
    logger.debug(msg)
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
