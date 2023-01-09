# -*- coding: utf8 -*-

import threading

from abc                         import ABC, abstractmethod
from loguru                      import logger

from bestiaire.utils.requests    import (
    api_internal_generic_request_get,
    resolver_move,
    )

from bestiaire.utils.computation import (
    closest_creature_from_creature,
    next_coords_to_creature,
    )


class Mob(ABC, threading.Thread):

    @abstractmethod
    def __init__(self):
        super(threading.Thread, self).__init__()

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
            ret = api_internal_generic_request_get(
                path=f"/creature/{self.id}"
            )
        except Exception as e:
            logger.error(f'{self.logh} | Request KO [{e}]')
        else:
            profile = ret['payload']

        if profile:
            self.x = profile['x']
            self.y = profile['y']
        else:
            self.x = None
            self.y = None
            logger.warning(f'{self.logh} | Query position KO')

        return (self.x, self.y)

    def set_pos(self):
        (closest, coords) = closest_creature_from_creature(self)
        if closest:
            # We have a close PC in sight
            (targetx, targety) = next_coords_to_creature(self, closest)
        else:
            logger.debug(f'{self.logh} | No close Creature. Stop here')
            return None

        if (targetx, targety) and \
           (self.x, self.y) == (targetx, targety):
            logger.debug(f"{self.logh} | Should not move "
                         f"(Already close to "
                         f"[{closest['id']}] {closest['name']} "
                         f"@({closest['x']},{closest['y']}))")
        elif (targetx, targety) in coords:
            # Collision check
            # There is an NPC on the path
            logger.debug(f"{self.logh} | Should not move "
                         f"(Path obstructed "
                         f"@({targetx, targety}))")
        else:
            # Lets call the resolver for move now
            logger.debug(f"{self.logh} | Move >> "
                         f"from (x:{self.x},y:{self.y}) "
                         f"to (x:{targetx},y:{targety}))")
            try:
                payload = resolver_move(self, targetx, targety)
            except Exception as e:
                logger.error(f'{self.logh} | Request KO [{e}]')
            else:
                if payload['result']['success']:
                    logger.debug(f"{self.logh} | Move OK "
                                 f"from (x:{self.x},y:{self.y}) "
                                 f"to (x:{targetx},y:{targety}))")
                else:
                    logger.warning(f"{self.logh} | Move KO "
                                   f"from (x:{self.x},y:{self.y}) "
                                   f"to (x:{targetx},y:{targety}))")

    @abstractmethod
    def get_life(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def get_pa(self):
        try:
            ret = api_internal_generic_request_get(
                path=f"/creature/{self.id}/pa"
            )
        except Exception as e:
            logger.error(f'{self.logh} | Request KO [{e}]')
        else:
            payload = ret['payload']
            self.blue = 0
            self.red  = 0

        if isinstance(payload['pa']['blue']['pa'], int) and \
           isinstance(payload['pa']['red']['pa'], int):
            self.blue = payload['pa']['blue']['pa']
            self.red  = payload['pa']['red']['pa']
        else:
            logger.warning(f'{self.logh} | Query PA KO')

        return (self.blue, self.red)

    # @abstractmethod
    # def move(self, dest):
