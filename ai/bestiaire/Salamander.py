# -*- coding: utf8 -*-

import time

from loguru                      import logger
from random                      import randint

from bestiaire.Mob               import Mob


class Salamander(Mob):
    def __init__(self, creature={}, stats={}, internal_name="default"):
        super(Mob, self).__init__()
        Mob.__init__(self)
        """
        {
            'account': None,
            'created': '2022-12-05 15:38:18',
            'date': '2022-12-05 15:38:18',
            'gender': True,
            'id': 'dcfe3118-8bd6-4ceb-b392-80bc09b0b35f',
            'instance': 'f128cf79-c9c3-4fe3-a227-29b960aa4cbf',
            'korp': None,
            'korp_rank': None,
            'level': 1,
            'name': 'Guerrier Salamandre',
            'race': 12,
            'rarity': 'Unique',
            'squad': None,
            'squad_rank': None,
            'targeted_by': None,
            'x': 4,
            'xp': 0,
            'y': 4,
        }
        """
        self.gender = creature['gender']
        self.hp = stats['def']['hp']
        self.hp_max = stats['def']['hpmax']
        self.id = creature['id']
        self.instance = creature['instance']
        self.level = creature['level']
        self.name = creature['name']
        self.race = creature['race']
        self.rarity = creature['rarity']
        self.targeted_by = creature['targeted_by']
        self.x = creature['x']
        self.xp = creature['xp']
        self.y = creature['y']
        # Addind Logging headers
        self.logh = f'[{self.id}] {self.name:20}'

    def run(self):
        SLEEP_TIME = 10

        while self.hp > 0:
            self.get_pa()
            self.get_pos()

            logger.debug(f'{self.logh} | Alive ({self.hp}HP) '
                         f'[🔴 :{self.red},🔵 :{self.blue}] '
                         f'@(x:{self.x},y:{self.y})')

            # MOVE
            if self.blue > 4 and randint(0, 1):
                self.set_pos()

            """
            # BASIC ATTACK
            if self.red > 8 and randint(0, 1):
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
                        logger.error(f'{self.logh} | Request KO [{e}]')
                    else:
                        if payload['result']['success']:
                            logger.debug(
                                f"{self.logh} | Attack OK "
                                f"([{closest['id']}] {closest['name']} "
                                f"@({closest['x']},{closest['y']}))"
                                )
                        else:
                            logger.warning(
                                f"{self.logh} | Attack KO "
                                f"([{closest['id']}] {closest['name']} "
                                f"@({closest['x']},{closest['y']}))"
                                )
                else:
                    # There is no NPC next to me
                    logger.debug(
                        f"{self.logh} | Cannot not attack "
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
        return self.hp

    def get_name(self):
        return self.internal_name
