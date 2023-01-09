# -*- coding: utf8 -*-

import math

from loguru                      import logger

from bestiaire.utils.requests    import api_internal_generic_request_get


def closest_creature_from_creature(self):
    # Lets find if we can co tawards someone
    try:
        ret = api_internal_generic_request_get(
            path=f"/creature/{self.id}/view"
        )
    except Exception as e:
        logger.error(f'Internal API Request KO [{e}]')
        return None
    else:
        creatures = ret['payload']

    if len(creatures) > 1:
        # There is Creatures in sight - Lets find the closest
        top = 100
        coords = []
        closest = None
        for creature in creatures:
            # We need the full list of (x,y) coords for collision checks
            coords.append((creature['x'], creature['y']))
            if creature['id'] == self.id:
                # We are seeing ourself -> NEXT
                continue
            elif creature['race'] > 10:
                # We do not move/attack towards another NPC
                pass
                # continue
            else:
                hypot = math.hypot(creature['x']-self.x, creature['y']-self.y)
                if hypot < top:
                    closest = creature
                    top = hypot

        """
        # Gruik: Fastest method, but tough to grab creature from this
        closest = min(coords,
                      key=lambda p: math.hypot(p[0]-self.x, p[1]-self.y))
        """
    elif len(creatures) == 1:
        closest = creatures[0]
    else:
        closest = None

    return (closest, coords)


def next_coords_to_creature(self, closest):
    # Lets try to move to closest creature
    if self.x == closest['x']:  # We are already on same X
        targetx = self.x
    elif self.x > closest['x']:
        if self.x - 1 == closest['x']:  # We are already close
            targetx = self.x
        else:
            targetx = self.x - 1
    elif self.x < closest['x']:
        if self.x + 1 == closest['x']:  # We are already close
            targetx = self.x
        else:
            targetx = self.x + 1

    if self.y == closest['y']:
        targety = self.y
    elif self.y > closest['y']:
        if self.y - 1 == closest['y']:  # We are already close
            targety = self.y
        else:
            targety = self.y - 1
    elif self.y < closest['y']:
        if self.y + 1 == closest['y']:  # We are already close
            targety = self.y
        else:
            targety = self.y + 1

    return (targetx, targety)
