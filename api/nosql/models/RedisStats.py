# -*- coding: utf8 -*-

from nosql.connector            import *

from mysql.methods.fn_creature  import fn_creature_get,fn_creature_stats_get
from mysql.methods.fn_inventory import fn_slots_get_all,fn_item_get_one

class RedisStats:
    def __init__(self,creature):
        RedisStats.key      = f'stats:{creature.id}:json'
        RedisStats.creature = creature

        try:
            if r.exists(RedisStats.key):
                # The pre-generated stats already exists in redis
                stats = json.loads(r.get(RedisStats.key))

                RedisStats.m = stats['base']['m']
                RedisStats.r = stats['base']['r']
                RedisStats.g = stats['base']['g']
                RedisStats.v = stats['base']['v']
                RedisStats.p = stats['base']['p']
                RedisStats.b = stats['base']['b']

                RedisStats.capcom = stats['off']['capcom']
                RedisStats.capsho = stats['off']['capsho']

                RedisStats.arm_b = stats['def']['armor']['b']
                RedisStats.arm_p = stats['def']['armor']['p']
                RedisStats.hpmax = stats['def']['hpmax']
                RedisStats.hp    = stats['def']['hp']
                RedisStats.dodge = stats['def']['dodge']
                RedisStats.parry = stats['def']['parry']
            else:
                logger.trace(f'Stats not in Redis cache')

                RedisStats.m = None
                RedisStats.r = None
                RedisStats.g = None
                RedisStats.v = None
                RedisStats.p = None
                RedisStats.b = None

                RedisStats.capcom = None
                RedisStats.capsho = None

                RedisStats.arm_b = None
                RedisStats.arm_p = None
                RedisStats.hpmax = None
                RedisStats.hp    = None
                RedisStats.dodge = None
                RedisStats.parry = None
        except Exception as e:
            logger.error(f'Method KO {e}')

    @classmethod
    def as_dict(cls):
        try:
            if RedisStats.m is None:
                logger.trace('RedisStats empty - Need refresh')
                return None

            # We push data in final dict
            RedisStats.dict = {"base":{
                                        "m": RedisStats.m,
                                        "r": RedisStats.r,
                                        "g": RedisStats.g,
                                        "v": RedisStats.v,
                                        "p": RedisStats.p,
                                        "b": RedisStats.b},
                              "off":{
                                        "capcom": RedisStats.capcom,
                                        "capsho": RedisStats.capsho},
                              "def":{
                                        "armor": {
                                                    "p": RedisStats.arm_p,
                                                    "b": RedisStats.arm_b},
                                        "hpmax": RedisStats.hpmax,
                                        "hp":    RedisStats.hp,
                                        "dodge": RedisStats.r,
                                        "parry": RedisStats.parry}}

        except Exception as e:
            logger.error(f'Method KO {e}')
            return None
        else:
            logger.trace(f'Method OK')
            return RedisStats.dict

    @classmethod
    def refresh(cls):
        try:
            cs = fn_creature_stats_get(RedisStats.creature)
            if cs:
                # We got Creature base stats
                RedisStats.m = cs.m_race + cs.m_class + cs.m_skill + cs.m_point
                RedisStats.r = cs.r_race + cs.r_class + cs.r_skill + cs.r_point
                RedisStats.g = cs.g_race + cs.g_class + cs.g_skill + cs.g_point
                RedisStats.v = cs.v_race + cs.v_class + cs.v_skill + cs.v_point
                RedisStats.p = cs.p_race + cs.p_class + cs.p_skill + cs.p_point
                RedisStats.b = cs.b_race + cs.b_class + cs.b_skill + cs.b_point
            else:
                # Something is probably wrong
                RedisStats.m = 0
                RedisStats.r = 0
                RedisStats.g = 0
                RedisStats.v = 0
                RedisStats.p = 0
                RedisStats.b = 0

            RedisStats.capcom = round((RedisStats.g + round((RedisStats.m + RedisStats.r)/2))/2)
            RedisStats.capsho = round((RedisStats.v + round((RedisStats.b + RedisStats.r)/2))/2)

            RedisStats.arm_b = RedisStats.arm_b
            RedisStats.arm_p = RedisStats.arm_p

            RedisStats.hpmax = 100 + RedisStats.m + round(RedisStats.creature.level/2)
            # For HP, we need to keep the data intact
            if r.exists(f'stats:{RedisStats.creature.id}:hp'):
                RedisStats.hp = int(r.get(f'stats:{RedisStats.creature.id}:hp'))
            else:
                r.set(f'stats:{RedisStats.creature.id}:hp',RedisStats.hpmax)

            RedisStats.dodge = RedisStats.r
            RedisStats.parry = round(((RedisStats.g-100)/50) * ((RedisStats.m-100)/50))

            # Working to find armor from equipped items
            RedisStats.arm_b = 0
            RedisStats.arm_p = 0
            slots = fn_slots_get_all(RedisStats.creature)[0]
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
                        RedisStats.arm_b += metaWeapon['arm_b']
                        RedisStats.arm_p += metaWeapon['arm_p']

            # We push data in final dict
            RedisStats.dict = {"base":{
                                        "m": 0 + RedisStats.m,
                                        "r": 0 + RedisStats.r,
                                        "g": 0 + RedisStats.g,
                                        "v": 0 + RedisStats.v,
                                        "p": 0 + RedisStats.p,
                                        "b": 0 + RedisStats.b},
                              "off":{
                                        "capcom": RedisStats.capcom,
                                        "capsho": RedisStats.capsho},
                              "def":{
                                        "armor": {
                                                    "p": RedisStats.arm_p,
                                                    "b": RedisStats.arm_b},
                                        "hpmax": RedisStats.hpmax,
                                        "hp":    RedisStats.hp,
                                        "dodge": RedisStats.r,
                                        "parry": RedisStats.parry}}

            r.set(RedisStats.key, json.dumps(RedisStats.dict), ex=300)
        except Exception as e:
            logger.error(f'Method KO {e}')
            return None
        else:
            logger.trace(f'Method OK')
            return RedisStats

    @classmethod
    def flush(cls):
        try:
            if r.exists(RedisStats.key):
                r.delete(RedisStats.key)
        except Exception as e:
            logger.error(f'Method KO {e}')
            return None
        else:
            logger.trace(f'Method OK')
            return True
