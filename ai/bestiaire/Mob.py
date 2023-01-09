# -*- coding: utf8 -*-

import threading

from abc                         import ABC, abstractmethod
from loguru                      import logger

from utils.requests              import resolver_move

from utils.computation import (
    closest_creature_from_creature,
    next_coords_to_creature,
    )

from nosql.models.RedisCreature  import RedisCreature
from nosql.models.RedisStats     import RedisStats
from nosql.models.RedisPa        import RedisPa


class Mob(ABC, threading.Thread):

    @abstractmethod
    def __init__(self, creatureuuid):
        super(threading.Thread, self).__init__()

        Creature = RedisCreature().get(creatureuuid)
        Stats = RedisStats(Creature)

        # We replicate Creature attibutes into Salamander
        self.creature = Creature
        # We add the HP/HPmax from Stats attributes
        self.stats = Stats
        # Addind Logging headers
        self.logh = f'[{self.creature.id}] {self.creature.name:20}'

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def attack(self):
        pass

    @abstractmethod
    def hit(self):
        pass

    def get_pos(self):
        try:
            Creature = RedisCreature().get(self.creature.id)
        except Exception as e:
            logger.error(f'{self.logh} | RedisCreature Request KO [{e}]')
        else:
            if Creature is not None and Creature is not False:
                self.creature = Creature
            logger.trace(f'{self.logh} | RedisCreature Request OK')

    def set_pos(self):
        (closest, coords) = closest_creature_from_creature(self)
        if closest:
            # We have a close PC in sight
            (targetx, targety) = next_coords_to_creature(self, closest)
        else:
            logger.debug(f'{self.logh} | No close Creature. Stop here')
            return None

        if (targetx, targety) and \
           (self.creature.x, self.creature.y) == (targetx, targety):
            logger.debug(
                f"{self.logh} | Should not move "
                f"(Already close to "
                f"[{closest['id']}] {closest['name']} "
                f"@({closest['x']},{closest['y']}))"
                )
        elif (targetx, targety) in coords:
            # Collision check
            # There is an NPC on the path
            logger.debug(
                f"{self.logh} | Should not move "
                f"(Path obstructed @({targetx, targety}))"
                )
        else:
            # Lets call the resolver for move now
            logger.debug(
                f"{self.logh} | Move >> "
                f"from (x:{self.creature.x},y:{self.creature.y}) "
                f"to (x:{targetx},y:{targety}))"
                )
            try:
                payload = resolver_move(self, targetx, targety)
            except Exception as e:
                logger.error(f'{self.logh} | Request KO [{e}]')
            else:
                if payload['result']['success']:
                    logger.debug(
                        f"{self.logh} | Move OK "
                        f"from (x:{self.creature.x},y:{self.creature.y}) "
                        f"to (x:{targetx},y:{targety}))"
                        )
                else:
                    logger.warning(
                        f"{self.logh} | Move KO "
                        f"from (x:{self.creature.x},y:{self.creature.y}) "
                        f"to (x:{targetx},y:{targety}))"
                        )

    @abstractmethod
    def get_life(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def get_pa(self):
        try:
            Pa = RedisPa(self.creature)
        except Exception as e:
            logger.error(f'{self.logh} | RedisPa Request KO [{e}]')
        else:
            if Pa is not False and Pa is not None:
                self.pa = Pa
            logger.trace(f'{self.logh} | RedisPa Request OK')

    # @abstractmethod
    # def move(self, dest):
