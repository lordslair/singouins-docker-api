# -*- coding: utf8 -*-

import copy
import json

from loguru                     import logger

from nosql.connector            import r

from mysql.methods.fn_creature  import fn_creature_stats_get
from mysql.methods.fn_inventory import fn_slots_get_all, fn_item_get_one


class RedisStats:
    def __init__(self, creature):
        self.hkey     = f'stats:{creature.id}'
        self.logh     = f'[Creature.id:{creature.id}]'

        if r.exists(self.hkey):
            # The pre-generated stats does already exist in redis
            try:
                hashdict = r.hgetall(self.hkey)
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                for k, v in hashdict.items():
                    # We create the object attribute with converted INT
                    setattr(self, k, int(v))
                # We need to do that as it is stored as 'hp' due to the Setter
                self._hp   = getattr(self, 'hp')

                logger.trace(f'{self.logh} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')
        else:
            # The pre-generated stats does not already exist in redis
            logger.trace(f'{self.logh} Method >> (HASH Creating)')

            try:
                cs = fn_creature_stats_get(creature)
                if cs:
                    # We got Creature base stats
                    self.m = cs.m_race + cs.m_class + cs.m_skill + cs.m_point
                    self.r = cs.r_race + cs.r_class + cs.r_skill + cs.r_point
                    self.g = cs.g_race + cs.g_class + cs.g_skill + cs.g_point
                    self.v = cs.v_race + cs.v_class + cs.v_skill + cs.v_point
                    self.p = cs.p_race + cs.p_class + cs.p_skill + cs.p_point
                    self.b = cs.b_race + cs.b_class + cs.b_skill + cs.b_point
                else:
                    # Something is probably wrong
                    self.m = 0
                    self.r = 0
                    self.g = 0
                    self.v = 0
                    self.p = 0
                    self.b = 0

                moymr       = round((self.m + self.r) / 2)
                self.capcom = round((self.g + moymr) / 2)
                moybr       = round((self.b + self.r) / 2)
                self.capsho = round((self.v + moybr) / 2)

                self.hpmax = 100 + self.m + round(creature.level / 2)
                self._hp   = self.hpmax
                self.hp    = self.hpmax

                self.dodge = self.r
                newg       = (self.g - 100) / 50
                newm       = (self.m - 100) / 50
                self.parry = round(newg * newm)
            except Exception as e:
                logger.error(f'{self.logh} Method KO '
                             f'(Building from Caracs) [{e}]')
            else:
                logger.trace(f'{self.logh} Method >> (Building from Caracs)')

            # Get the metaWeapons
            if r.exists('system:meta:weapon'):
                metaWeapons = json.loads(r.get('system:meta:weapon'))
                logger.trace(f'{self.logh} Method >> metaWeapons OK')
            else:
                logger.warning(f'{self.logh} Method >> metaWeapons KO')
                return False

            try:
                # Working to find armor from equipped items
                self.arm_b = 0
                self.arm_p = 0
                slots = fn_slots_get_all(creature)
                if slots:
                    armors     = [fn_item_get_one(slots.feet),
                                  fn_item_get_one(slots.hands),
                                  fn_item_get_one(slots.head),
                                  fn_item_get_one(slots.shoulders),
                                  fn_item_get_one(slots.torso),
                                  fn_item_get_one(slots.legs)]

                    for armor in armors:
                        if armor is not None:
                            result = filter(lambda x: x["id"] == armor.metaid,
                                            metaWeapons)
                            metaWeapon = dict(list(result)[0])  # Gruikfix
                            self.arm_b += metaWeapon['arm_b']
                            self.arm_p += metaWeapon['arm_p']
                else:
                    logger.warning(f'{self.logh} Method >> Slots Not Found')
            except Exception as e:
                logger.error(f'{self.logh} Method KO '
                             f'(Building from Equipment) [{e}]')
            else:
                logger.trace(f'{self.logh} Method >> '
                             f'(Building from Equipment)')

            try:
                # We push data in final dict
                logger.trace(f'{self.logh} Method >> (Storing HASH)')
                clone = copy.deepcopy(self)
                if clone.hkey:
                    del clone.hkey
                if clone.logh:
                    del clone.logh
                if clone._hp:
                    del clone._hp
                hashdict = clone.__dict__

                r.hset(self.hkey, mapping=hashdict)
            except Exception as e:
                logger.error(f'{self.logh} Method KO (Storing HASH) [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')

    def destroy(self):
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(self.hkey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        hashdict = {
            "base": {
                "m": self.m,
                "r": self.r,
                "g": self.g,
                "v": self.v,
                "p": self.p,
                "b": self.b
            },
            "off": {
                "capcom": self.capcom,
                "capsho": self.capsho,
            },
            "def": {
                "armor": {
                    "p": self.arm_p,
                    "b": self.arm_b,
                },
                "hpmax": self.hpmax,
                "hp": self._hp,
                "dodge": self.r,
                "parry": self.parry,
            }
        }
        return hashdict

    """
    Getter/Setter block for HP management
    It is done that way to r.hset() every time API code manipulates Creature HP
    And avoid to build a store() method just for that purpose
    As it is the only value that can be directly modified in the RedisStats
    """
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, hp):
        self._hp = hp
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) HP')
            r.hset(self.hkey, 'hp', self._hp)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')
