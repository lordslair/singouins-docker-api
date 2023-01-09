# -*- coding: utf8 -*-

import math

from loguru                      import logger

from nosql.models.RedisCreature  import RedisCreature


def closest_creature_from_creature(self):
    # Lets find if we can co tawards someone
    try:
        # Grab the view
        range = 4 + round(self.stats.p / 50)

        maxx  = self.creature.x + range
        minx  = self.creature.x - range
        maxy  = self.creature.y + range
        miny  = self.creature.y - range

        Creatures = RedisCreature().search(
            query=f'(@x:[{minx} {maxx}]) & (@y:[{miny} {maxy}])',
            )
    except Exception as e:
        logger.error(f'Calculating View KO [{e}]')
        return None

    if len(Creatures) > 1:
        # There is Creatures in sight - Lets find the closest
        top = 100
        coords = []
        closest = None
        for creature in Creatures:
            # We need the full list of (x,y) coords for collision checks
            coords.append((creature['x'], creature['y']))
            if creature['id'] == self.creature.id:
                # We are seeing ourself -> NEXT
                continue
            elif creature['race'] > 10:
                # We do not move/attack towards another NPC
                pass
                # continue
            else:
                hypot = math.hypot(
                    creature['x'] - self.creature.x,
                    creature['y'] - self.creature.y
                    )
                if hypot < top:
                    closest = creature
                    top = hypot

        """
        # Gruik: Fastest method, but tough to grab creature from this
        closest = min(
            coords,
            key=lambda p: math.hypot(
                p[0]-self.creature.x,
                p[1]-self.creature.y
                )
            )
        """
    elif len(Creatures) == 1:
        closest = Creatures[0]
        coords = None
    else:
        closest = None
        coords = None

    return (closest, coords)


def next_coords_to_creature(self, closest):
    # Lets try to move to closest creature
    if self.creature.x == closest['x']:  # We are already on same X
        targetx = self.creature.x
    elif self.creature.x > closest['x']:
        if self.creature.x - 1 == closest['x']:  # We are already close
            targetx = self.creature.x
        else:
            targetx = self.creature.x - 1
    elif self.creature.x < closest['x']:
        if self.creature.x + 1 == closest['x']:  # We are already close
            targetx = self.creature.x
        else:
            targetx = self.creature.x + 1

    if self.creature.y == closest['y']:
        targety = self.creature.y
    elif self.creature.y > closest['y']:
        if self.creature.y - 1 == closest['y']:  # We are already close
            targety = self.creature.y
        else:
            targety = self.creature.y - 1
    elif self.creature.y < closest['y']:
        if self.creature.y + 1 == closest['y']:  # We are already close
            targety = self.creature.y
        else:
            targety = self.creature.y + 1

    return (targetx, targety)
