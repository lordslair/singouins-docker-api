# -*- coding: utf8 -*-

import random

from flask import g
from loguru import logger
from mongoengine import Q

from mongo.models.Creature import CreatureDocument


def get_empty_coords(minx=1, miny=1, maxx=5, maxy=5):
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
