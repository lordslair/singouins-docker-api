# -*- coding: utf8 -*-

import math

from loguru import logger

from nosql.models.RedisSearch import RedisSearch


def closest_player_from_me(self):
    """
    Fetchs the closest PC using a RedisSearch.

    Parameters: None

    Returns:
        - RedisCreature
    """
    try:
        # Grab the view
        range = 4 + round(self.stats.p / 50)

        maxx  = self.creature.x + range
        minx  = self.creature.x - range
        maxy  = self.creature.y + range
        miny  = self.creature.y - range

        Creatures = RedisSearch().creature(
            query=(
                f'(@x:[{minx} {maxx}]) & '
                # ^ We look for Creatures BETWEEN minx and maxx
                f'(@y:[{miny} {maxy}]) & '
                # ^ We look for Creatures BETWEEN miny and maxy
                f'-(@account:None)'
                # ^ We exclude ALL NPC
                ),
            )
    except Exception as e:
        logger.error(f'Calculating View KO [{e}]')
        return None

    if len(Creatures.results) > 1:
        # There are Creatures in sight - Lets find if someone has aggro
        Creatures.results.sort(key=lambda x: x.aggro, reverse=True)
        if Creatures.results[0].aggro > 0:
            # This Creature in sight has the biggest aggro
            # We move towards it
            CreatureTarget = Creatures.results[0]
            logger.trace(
                f'Target found via aggro({CreatureTarget.aggro}): '
                f'[{CreatureTarget.id}] {CreatureTarget.name} '
                f'@({CreatureTarget.x}, {CreatureTarget.y})'
                )
        else:
            # There are Creatures in sight - Lets find the closest
            top = 100
            CreatureTarget = None
            for Creature in Creatures.results:
                if Creature.id == self.creature.id:
                    # We are seeing ourself -> NEXT
                    continue
                elif Creature.race > 10:
                    # We do not move/attack towards another NPC
                    pass
                    # continue
                else:
                    hypot = math.hypot(
                        Creature.x - self.creature.x,
                        Creature.y - self.creature.y
                        )
                    if hypot < top:
                        CreatureTarget = Creature
                        top = hypot
    elif len(Creatures.results) == 1:
        CreatureTarget = Creatures.results[0]
    else:
        CreatureTarget = None

    return CreatureTarget


def next_coords_to_creature(self, CreatureTarget):
    """
    Finds the next hop towards a Creature.

    Parameters:
        - CreatureTarget: RedisCreature Object

    Returns: (x, y)
    """
    # Lets try to move to closest creature
    if self.creature.x == CreatureTarget.x:  # We are already on same X
        x = self.creature.x
    elif self.creature.x > CreatureTarget.x:
        if self.creature.x - 1 == CreatureTarget.x:  # We are already close
            x = self.creature.x
        else:
            x = self.creature.x - 1
    elif self.creature.x < CreatureTarget.x:
        if self.creature.x + 1 == CreatureTarget.x:  # We are already close
            x = self.creature.x
        else:
            x = self.creature.x + 1

    if self.creature.y == CreatureTarget.y:  # We are already on same Y
        y = self.creature.y
    elif self.creature.y > CreatureTarget.y:
        if self.creature.y - 1 == CreatureTarget.y:  # We are already close
            y = self.creature.y
        else:
            y = self.creature.y - 1
    elif self.creature.y < CreatureTarget.y:
        if self.creature.y + 1 == CreatureTarget.y:  # We are already close
            y = self.creature.y
        else:
            y = self.creature.y + 1

    return (x, y)


def is_coords_empty(x, y):
    """
    Checks if a set of coordinates is empty or not.

    Parameters:
        - x: INT
        - y: INT

    Returns: bool()
    """
    try:
        Creatures = RedisSearch().creature(
            query=f'(@x:[{x} {x}]) & (@y:[{y} {y}])'
            )
    except Exception as e:
        logger.error(f'Calculating View KO [{e}]')
        return None
    else:
        if len(Creatures.results) == 0:
            # No Creature is on this set of coordinates
            return True
        else:
            # A Creature is on this set of coordinates
            return False
