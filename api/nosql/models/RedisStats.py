# -*- coding: utf8 -*-

from nosql.connector            import *

from mysql.methods.fn_creature  import fn_creature_get,fn_creature_stats_get
from mysql.methods.fn_inventory import fn_slots_get_all,fn_item_get_one

class RedisStats:
    def __init__(self,creature):
        self.hkey     = f'stats:{creature.id}'
        self.logh     = f'[creature.id:{creature.id}]'

        if r.exists(self.hkey):
            # The pre-generated stats does already exist in redis
            try:
                hash = r.hgetall(self.hkey)
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                self.m      = int(hash['m'])
                self.r      = int(hash['r'])
                self.g      = int(hash['g'])
                self.v      = int(hash['v'])
                self.p      = int(hash['p'])
                self.b      = int(hash['b'])
                self.capcom = int(hash['capcom'])
                self.capsho = int(hash['capsho'])
                self.arm_p  = int(hash['arm_p'])
                self.arm_b  = int(hash['arm_b'])
                self.hpmax  = int(hash['hpmax'])
                self.hp     = int(hash['hp'])
                self.r      = int(hash['r'])
                self.parry  = int(hash['parry'])

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

                self.capcom = round((self.g + round((self.m + self.r)/2))/2)
                self.capsho = round((self.v + round((self.b + self.r)/2))/2)

                self.hpmax = 100 + self.m + round(creature.level/2)
                self.hp    = self.hpmax

                self.dodge = self.r
                self.parry = round(((self.g-100)/50) * ((self.m-100)/50))

                # Working to find armor from equipped items
                self.arm_b = 0
                self.arm_p = 0
                slots = fn_slots_get_all(creature)[0]
                if slots:
                    armormetas = []
                    armors     = [fn_item_get_one(slots.feet),
                                  fn_item_get_one(slots.hands),
                                  fn_item_get_one(slots.head),
                                  fn_item_get_one(slots.shoulders),
                                  fn_item_get_one(slots.torso),
                                  fn_item_get_one(slots.legs)]

                    for armor in armors:
                        if armor is not None:
                            metaWeapon = dict(list(filter(lambda x:x["id"] == armor.metaid,metaWeapons))[0]) # Gruikfix
                            self.arm_b += metaWeapon['arm_b']
                            self.arm_p += metaWeapon['arm_p']

                # We push data in final dict
                logger.trace(f'{self.logh} Method >> (Storing HASH)')
                hashdict = {"m":      0 + self.m,
                            "r":      0 + self.r,
                            "g":      0 + self.g,
                            "v":      0 + self.v,
                            "p":      0 + self.p,
                            "b":      0 + self.b,
                            "capcom": self.capcom,
                            "capsho": self.capsho,
                            "arm_p":  self.arm_p,
                            "arm_b":  self.arm_b,
                            "hpmax":  self.hpmax,
                            "hp":     self.hp,
                            "dodge":  self.r,
                            "parry":  self.parry}

                r.hmset(self.hkey, hashdict)
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')

        # Whatever the scenarion, We push data in the object
        try:
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            self.dict = {"base":{
                                        "m": self.m,
                                        "r": self.r,
                                        "g": self.g,
                                        "v": self.v,
                                        "p": self.p,
                                        "b": self.b
                                },
                              "off":{
                                        "capcom": self.capcom,
                                        "capsho": self.capsho
                                    },
                              "def":{
                                        "armor":{
                                                    "p": self.arm_p,
                                                    "b": self.arm_b
                                                },
                                        "hpmax": self.hpmax,
                                        "hp":    self.hp,
                                        "dodge": self.r,
                                        "parry": self.parry
                                    }
                              }
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    def store(self):
        try:
            # We push data in final dict
            hashdict =  {
                            "m":      self.m,
                            "r":      self.r,
                            "g":      self.g,
                            "v":      self.v,
                            "p":      self.p,
                            "b":      self.b,
                            "capcom": self.capcom,
                            "capsho": self.capsho,
                            "arm_p":  self.arm_p,
                            "arm_b":  self.arm_b,
                            "hpmax":  self.hpmax,
                            "hp":     self.hp,
                            "dodge":  self.r,
                            "parry":  self.parry
                        }
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            r.hmset(self.hkey, hashdict)
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self):
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.del(self.hkey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True
