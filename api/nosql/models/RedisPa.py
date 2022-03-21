# -*- coding: utf8 -*-

from mysql.methods.fn_creature  import fn_creature_get
from nosql.connector            import *

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

class RedisPa:
    def __init__(self,creature):
        RedisPa.all      = {"blue": {"pa":    None,
                                     "ttnpa": None,
                                     "ttl":   None},
                            "red":  {"pa":    None,
                                     "ttnpa": None,
                                     "ttl":   None}}
        RedisPa.creature = creature
        RedisPa.logh     = f'[creature.id:{RedisPa.creature.id}]'

    @classmethod
    def set(cls,redpa,bluepa):
        try:
            if bluepa > 0:
                # An action consumed a blue PA, we need to update
                key    = f'blue:{RedisPa.creature.id}'
                ttl    = r.ttl(key)
                newttl = ttl + (bluepa * bluepaduration)

                if ttl > 0:
                    # Key still exists (PA count < PA max)
                    r.expire(key,newttl)
                else:
                    # Key does not exist anymore (PA count = PA max)
                    r.set(key,'',ex=newttl)
            if redpa > 0:
                # An action consumed a red PA, we need to update
                key    = f'red:{RedisPa.creature.id}'
                ttl    = r.ttl(key)
                newttl = ttl + (redpa * redpaduration)

                if ttl > 0:
                    # Key still exists (PA count < PA max)
                    r.expire(key,newttl)
                else:
                    # Key does not exist anymore (PA count = PA max)
                    r.set(key,'',ex=newttl)
        except Exception as e:
            logger.error(f'{RedisPa.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{RedisPa.logh} Method OK')
            return True

    @classmethod
    def get(cls):
        try:
            redkey    = f'red:{RedisPa.creature.id}'
            redttl    = r.ttl(redkey)
            red       = {"pa":    int(round(((redmaxttl - abs(redttl))  / redpaduration))),
                         "ttnpa": r.ttl(redkey) % redpaduration,
                         "ttl":   redttl}

            bluekey   = f'blue:{RedisPa.creature.id}'
            bluettl   = r.ttl(bluekey)
            blue      = {"pa":    int(round(((bluemaxttl - abs(bluettl))  / bluepaduration))),
                         "ttnpa": r.ttl(bluekey) % bluepaduration,
                         "ttl":   bluettl}

            all       = {"red":  red,
                         "blue": blue}
        except Exception as e:
            logger.error(f'{RedisPa.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{RedisPa.logh} Method OK')
            return all

    @classmethod
    def reset(cls):
        try:
            r.set(f'red:{RedisPa.creature.id}', 'red', ex=1)
            r.set(f'blue:{RedisPa.creature.id}','blue',ex=1)
        except Exception as e:
            logger.error(f'{RedisPa.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{RedisPa.logh} Method OK')
            return True
