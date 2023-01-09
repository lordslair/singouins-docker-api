# -*- coding: utf8 -*-

import time

from loguru                      import logger
from random                      import randint

from bestiaire.Mob               import Mob


class Fungus(Mob):
    def __init__(self, creatureuuid, internal_name="default"):
        super(Mob, self).__init__()
        Mob.__init__(self, creatureuuid)

    def run(self):
        SLEEP_TIME = 10

        while self.stats.hp > 0:
            self.get_pa()
            self.get_pos()

            logger.debug(
                f'{self.logh} | Alive ({self.stats.hp}HP) '
                f'[🔴 :{self.pa.redpa},🔵 :{self.pa.bluepa}] '
                f'@(x:{self.creature.x},y:{self.creature.y})'
                )

            # MOVE
            if self.pa.bluepa > 4 and randint(0, 1):
                self.set_pos()

            """
            # BASIC ATTACK
            if self.pa.redpa > 8 and randint(0, 1):
                # We check if something is nearby
                (closest, coords) = closest_creature_from_creature(self)
                if (self.x - 1 <= closest['x'] <= self.x + 1 and
                        self.y - 1 <= closest['y'] <= self.y + 1):
                    # The closest creature is in range for basic attack
                    logger.debug(f"{self.logh} | Attack >> "
                                 f"([{closest['id']}] {closest['name']} "
                                 f"@({closest['x']},{closest['y']}))")
                    try:
                        payload = resolver_basic_attack(self, closest)
                    except Exception as e:
                        logger.error(f'{h} | Request KO [{e}]')
                    else:
                        if payload['result']['success']:
                            logger.debug(
                                f"{h} | Attack OK "
                                f"([{closest['id']}] {closest['name']} "
                                f"@({closest['x']},{closest['y']}))"
                                )
                        else:
                            logger.warning(
                                f"{h} | Attack KO "
                                f"([{closest['id']}] {closest['name']} "
                                f"@({closest['x']},{closest['y']}))"
                                )
                else:
                    # There is no NPC next to me
                    logger.debug(
                        f"{h} | Cannot not attack "
                        f"(Target too far"
                        f"@({closest['x'], closest['y']}))"
                        )
        """
            time.sleep(SLEEP_TIME)
        return

    def attack(self):
        pass

    def hit(self):
        pass

    def get_life(self):
        return self.stats.hp

    def get_name(self):
        return self.internal_name
