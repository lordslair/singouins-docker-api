# -*- coding: utf8 -*-

import threading

from abc                         import ABC, abstractmethod
from loguru                      import logger

from utils.requests              import resolver_move

from utils.computation import (
    closest_player_from_me,
    next_coords_to_creature,
    is_coords_empty,
    )

from nosql.models.RedisCreature  import RedisCreature
from nosql.models.RedisStats     import RedisStats
from nosql.models.RedisPa        import RedisPa
from nosql.models.RedisInstance  import RedisInstance


class Mob(ABC, threading.Thread):

    @abstractmethod
    def __init__(self, creatureuuid):
        super(threading.Thread, self).__init__()

        # We replicate Creature attibutes into Salamander
        self.creature = RedisCreature(creatureuuid=creatureuuid)
        # We add the HP/HPmax from Stats attributes
        self.stats = RedisStats(creatureuuid=self.creature.id)
        # We add Instance info as we need it
        self.instance = RedisInstance(instanceuuid=self.creature.instance)
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
            Creature = RedisCreature(creatureuuid=self.creature.id)
        except Exception as e:
            logger.error(f'{self.logh} | RedisCreature Request KO [{e}]')
        else:
            if Creature is not None and Creature is not False:
                self.creature = Creature
            logger.trace(f'{self.logh} | RedisCreature Request OK')

    def set_pos(self):
        # We check the closest PC in sight
        CreatureTarget = closest_player_from_me(self)
        if CreatureTarget:
            # We have a close PC in sight
            (nextx, nexty) = next_coords_to_creature(self, CreatureTarget)
        else:
            logger.debug(f'{self.logh} | No close Creature. Stop here')
            return None

        # logger.info(f'closest:{CreatureTarget}')
        # logger.info(f'x:{nextx}, y:{nexty}')

        # Collision check
        if not is_coords_empty(x=nextx, y=nexty):
            # There is a Creature on these coordinates
            logger.debug(
                f"{self.logh} | Move KO | "
                f'(Tile occupied @({nextx}, {nexty}))'
                )
            return
        else:
            # There is no one on these coordinates
            logger.debug(
                f"{self.logh} | Move >> | "
                f'(Tile empty @({nextx, nexty}))'
                )

        # Proximity check
        if (nextx, nexty) and \
           (self.creature.x, self.creature.y) == (nextx, nexty):
            logger.debug(
                f"{self.logh} | Move KO | "
                f"(Already close to "
                f"[{CreatureTarget.id}] {CreatureTarget.name} "
                f"@({CreatureTarget.x},{CreatureTarget.y}))"
                )
            return
        else:
            logger.debug(
                f"{self.logh} | Move >> | "
                f"(Not close enough to "
                f"[{CreatureTarget.id}] {CreatureTarget.name} "
                f"@({CreatureTarget.x},{CreatureTarget.y}))"
                )

        # We can move, path clear
        logger.debug(
            f"{self.logh} | Move >> | "
            f"from (x:{self.creature.x},y:{self.creature.y}) "
            f"to (x:{nextx},y:{nextx}))"
            )
        try:
            payload = resolver_move(self, nextx, nexty)
        except Exception as e:
            logger.error(f'{self.logh} | Request KO [{e}]')
        else:
            if payload is None:
                logger.warning(
                    f"{self.logh} | Move KO | "
                    'Resolver response.body is None'
                    )
                return

            if payload['result']['success']:
                logger.debug(
                    f"{self.logh} | Move OK | "
                    f"from (x:{self.creature.x},y:{self.creature.y}) "
                    f"to (x:{nextx},y:{nexty}))"
                    )
            else:
                logger.warning(
                    f"{self.logh} | Move KO | "
                    f"from (x:{self.creature.x},y:{self.creature.y}) "
                    f"to (x:{nextx},y:{nexty}))"
                    )

    @abstractmethod
    def get_life(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def get_pa(self):
        try:
            Pa = RedisPa(creatureuuid=self.creature.id)
        except Exception as e:
            logger.error(f'{self.logh} | RedisPa Request KO [{e}]')
        else:
            if Pa is not False and Pa is not None:
                self.pa = Pa
            logger.trace(f'{self.logh} | RedisPa Request OK')

    # @abstractmethod
    # def move(self, dest):
