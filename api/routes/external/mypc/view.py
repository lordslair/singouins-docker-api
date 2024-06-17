# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q

from mongo.models.Creature import CreatureDocument
from mongo.models.Corpse import CorpseDocument
from mongo.models.Resource import ResourceDocument

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/view/*
#
# API: GET /mypc/<uuid:creatureuuid>/view
@jwt_required()
# Custom decorators
@check_creature_exists
def view_get(creatureuuid):

    if hasattr(g.Creature, 'instance'):
        logger.trace(f'{g.h} Creature in an Instance:{g.Creature.instance}')
    else:
        # Creature is not in an instance, view is empty
        logger.trace(f'{g.h} Creature not in an Instance')
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

    if g.Creature.squad.id:
        logger.trace(f'{g.h} Creature in an Squad:{g.Creature.squad.id}')
        try:
            query = (
                Q(squad__id=g.Creature.squad.id) &
                Q(instance=g.Creature.instance) &
                Q(squad__rank__ne="Pending")
                )
            SquadMembers = CreatureDocument.objects(query)
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
        except CreatureDocument.DoesNotExist:
            msg = (f'{g.h} Squad({g.Creature.squad.id}) Query KO (404)')
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.trace(f'{g.h} Squad({g.Creature.squad.id}) Query OK')

        try:
            CreaturesUnduplicated = []  # We initialize the result array
            ResourcesUnduplicated = []  # We initialize the result array
            CorpsesUnduplicated = []  # We initialize the result array

            for SquadMember in SquadMembers:
                range = 4 + round(g.Creature.stats.total.p / 50)
                query_view = (
                    Q(instance=g.Creature.instance) &
                    Q(x__gte=SquadMember.x - range) &
                    Q(x__lte=SquadMember.x + range) &
                    Q(y__gte=SquadMember.y - range) &
                    Q(y__lte=SquadMember.y + range)
                    )

                # We do the job for Creatures
                CreaturesSeen = CreatureDocument.objects(query_view)
                CreaturesCount = CreaturesSeen.count()
                if CreaturesCount > 0:
                    logger.trace(f'[{SquadMember.id}] {SquadMember.name} (sees:{CreaturesCount})')
                    CreaturesUnduplicated.extend(list(CreaturesSeen))
                # We do the job for Corpses
                CorpsesSeen = CorpseDocument.objects(query_view)
                CorpsesCount = CorpsesSeen.count()
                if CorpsesCount > 0:
                    logger.trace(f'[{SquadMember.id}] {SquadMember.name} (sees:{CorpsesCount})')
                    CorpsesUnduplicated.extend(list(CorpsesSeen))
                # We do the job for Resources
                ResourcesSeen = ResourceDocument.objects(query_view)
                ResourcesCount = ResourcesSeen.count()
                if ResourcesCount > 0:
                    logger.trace(f'[{SquadMember.id}] {SquadMember.name} (sees:{ResourcesCount})')
                    ResourcesUnduplicated.extend(list(ResourcesSeen))

            # Use a dictionary to remove duplicates based on the _id field
            Creatures = {Creature._id: Creature for Creature in CreaturesUnduplicated}.values()
            Corpses = {Corpse._id: Corpse for Corpse in CorpsesUnduplicated}.values()
            Resources = {Resource._id: Resource for Resource in ResourcesUnduplicated}.values()
        except Exception as e:
            msg = (f'{g.h} Squad({g.Creature.squad.id}) View Query KO [{e}]')
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
            range = 4 + round(g.Creature.stats.total.p / 50)
            query_view = (
                Q(instance=g.Creature.instance) &
                Q(x__gte=g.Creature.x - range) &
                Q(x__lte=g.Creature.x + range) &
                Q(y__gte=g.Creature.y - range) &
                Q(y__lte=g.Creature.y + range)
                )

            Creatures = CreatureDocument.objects(query_view)
            Corpses = CorpseDocument.objects(query_view)
            Resources = ResourceDocument.objects(query_view)
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
                "creatures": [Creature.to_mongo() for Creature in Creatures],
                "corpses": [Corpse.to_mongo() for Corpse in Corpses],
                "resources": [Resource.to_mongo() for Resource in Resources],
            },
        }
    ), 200
