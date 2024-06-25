# -*- coding: utf8 -*-

import datetime
import json
import random
import uuid

from flask import g, jsonify, request
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q
from random import choices, randint

from mongo.models.Creature import (
    CreatureDocument,
    CreatureHP,
    CreatureSlots,
    CreatureStats,
    CreatureStatsType,
    CreatureSquad,
    CreatureKorp,
)
from mongo.models.Instance import InstanceDocument

from nosql.connector import r
from nosql.maps import get_map
from nosql.queue import yqueue_put
from nosql.metas import metaNames

from utils.decorators import (
    check_creature_exists,
    check_is_json,
    )

from variables import YQ_DISCORD


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: PUT /mypc/<uuid:creatureuuid>/instance
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
def add(creatureuuid):
    hardcore = request.json.get('hardcore', None)
    fast     = request.json.get('fast', None)
    mapid    = request.json.get('mapid', None)
    public   = request.json.get('public', None)

    if not isinstance(mapid, int):
        msg = f'{g.h} Map ID should be an INT (mapid:{mapid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(hardcore, bool):
        msg = f'{g.h} Hardcore param should be a boolean (hardcore:{hardcore})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(fast, bool):
        msg = f'{g.h} Fast param should be a boolean (hardcore:{hardcore})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(public, bool):
        msg = f'{g.h} Public param should be a boolean (hardcore:{hardcore})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Check if map related to mapid exists
    try:
        map = get_map(mapid)
    except Exception as e:
        msg = f'{g.h} Map Query KO (mapid:{mapid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Create the new instance
    try:
        newInstance = InstanceDocument(
            creator=g.Creature.id,
            fast=fast,
            hardcore=hardcore,
            map=mapid,
            public=public,
            )
        newInstance.save()

        g.Creature.instance = newInstance.id
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
    except Exception as e:
        msg = f"{g.h} Instance Query KO [{e}]"
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Everything went well, creation DONE
    # We put the info in queue for Discord
    scopes = []
    if hasattr(g.Creature.korp, 'id'):
        scopes.append(f'Korp-{g.Creature.korp.id}')
    if hasattr(g.Creature.korp, 'id'):
        scopes.append(f'Squad-{g.Creature.squad.id}')
    for scope in scopes:
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':map: **[{g.Creature.id}] {g.Creature.name}** '
                    f'opened an Instance ({newInstance.id})'
                    ),
                "embed": None,
                "scope": scope,
                }
            )
    # We need to create the mobs to populate the instance
    (mapx, mapy) = map['size'].split('x')
    mobs_nbr = 1
    rarities = [
        'Small',
        'Medium',
        'Big',
        'Unique',
        'Boss',
        'God',
    ]

    try:
        while mobs_nbr < 4:
            try:
                #
                raceid = randint(11, 16)
                gender = randint(0, 1)
                rarity = choices(rarities,
                                 weights=(20, 30, 20, 10, 15, 5),
                                 k=1)[0]
                x = randint(1, int(mapx))
                y = randint(1, int(mapy))

                # We grab the race wanted from metaRaces
                metaRace = metaNames['race'][raceid]
                if metaRace is None:
                    msg = f'{g.h} MetaRace not found (race:{raceid})'
                    logger.warning(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200

                newMonster = CreatureDocument(
                    _id=uuid.uuid4(),
                    gender=gender,
                    hp=CreatureHP(
                        base=metaRace['min_m'] + 100,
                        current=metaRace['min_m'] + 100,
                        max=metaRace['min_m'] + 100,
                        ),
                    instance=newInstance.id,
                    korp=CreatureKorp(),
                    name=metaNames['race'][raceid]['name'],
                    race=raceid,
                    rarity=rarity,
                    squad=CreatureSquad(),
                    slots=CreatureSlots(),
                    stats=CreatureStats(
                        spec=CreatureStatsType(),
                        race=CreatureStatsType(
                            b=metaRace['min_b'],
                            g=metaRace['min_g'],
                            m=metaRace['min_m'],
                            p=metaRace['min_p'],
                            r=metaRace['min_r'],
                            v=metaRace['min_v'],
                        ),
                        total=CreatureStatsType(
                            b=metaRace['min_b'],
                            g=metaRace['min_g'],
                            m=metaRace['min_m'],
                            p=metaRace['min_p'],
                            r=metaRace['min_r'],
                            v=metaRace['min_v'],
                        ),
                    ),
                    x=x,
                    y=y,
                )
                newMonster.save()
            except Exception as e:
                msg = (f'{g.h} Population in Instance KO for mob '
                       f'#{mobs_nbr} [{e}]')
                logger.error(msg)
            else:
                # We send in pubsub channel for IA to spawn the Mobs
                try:
                    r.publish(
                        'ai-creature',
                        json.dumps({
                            "action": 'pop',
                            "instance": newInstance.to_json(),
                            "creature": newMonster.to_json(),
                            }),
                        )
                except Exception as e:
                    msg = f'{g.h} Publish(ai-creature/pop) KO [{e}]'
                    logger.error(msg)

            mobs_nbr += 1
    except Exception as e:
        msg = f'{g.h} Instance({newInstance.id}) Population KO [{e}]'
        logger.error(msg)

    try:
        # We find an empty spot to land the Creature
        (x, y) = get_empty_coords()

        g.Creature.x = x
        g.Creature.y = y
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
    except Exception as e:
        msg = f"{g.h} Creature Query KO [{e}]"
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Finally everything is done
    msg = f'{g.h} Instance({newInstance.id}) Create OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": newInstance.to_mongo(),
        }
    ), 201


def get_empty_coords(minx=0, miny=0, maxx=5, maxy=5):
    """
    Finds an empty set of coordinates within a given range.

    Parameters:
        - minx: Minimum x coordinate (inclusive)
        - miny: Minimum y coordinate (inclusive)
        - maxx: Maximum x coordinate (inclusive)
        - maxy: Maximum y coordinate (inclusive)

    Returns:
        A tuple of the coordinates (x, y) that are free.
    """
    occupied_spots = set()
    free_spots = []
    try:
        query_view = (
            Q(instance=g.Creature.instance) &
            Q(x__gte=minx) &
            Q(x__lte=maxx) &
            Q(y__gte=miny) &
            Q(y__lte=maxy)
            )

        # We do the job for Creatures
        Creatures = CreatureDocument.objects(query_view)

        for Creature in Creatures:
            occupied_spots.add((Creature.x, Creature.y))
    except Exception as e:
        logger.error(f'{g.h} | CreatureDocument Query KO [{e}]')

    # Find free spots within the specified range
    free_spots = [
        (x, y)
        for x in range(minx, maxx + 1)
        for y in range(miny, maxy + 1)
        if (x, y) not in occupied_spots
    ]

    if not free_spots:
        raise ValueError("No free spots available within the specified range")

    # We pull out a random position from the free_spots
    free_spot = random.choice(free_spots)
    logger.debug(f'{g.h} FOUND free_spot: {free_spot}')
    return free_spot
