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
    def __init__(self):
        self.all  = {"red": {"pa":     None,
                             "ttnpa":  None,
                             "ttl":    None},
                     "blue": {"pa":    None,
                              "ttnpa": None,
                              "ttl":   None}}

    @classmethod
    def set(cls,creature,redpa,bluepa):
        try:
            if bluepa > 0:
                # An action consumed a blue PA, we need to update
                key    = f'blue:{creature.id}'
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
                key    = f'red:{creature.id}'
                ttl    = r.ttl(key)
                newttl = ttl + (redpa * redpaduration)

                if ttl > 0:
                    # Key still exists (PA count < PA max)
                    r.expire(key,newttl)
                else:
                    # Key does not exist anymore (PA count = PA max)
                    r.set(key,'',ex=newttl)
        except Exception as e:
            logger.error(f'Method KO {e}')
            return None
        else:
            logger.trace(f'Method OK')
            return True

    @classmethod
    def get(cls,creature):
        try:
            redkey    = f'red:{creature.id}'
            redttl    = r.ttl(redkey)
            red  = {"pa":    int(round(((redmaxttl - abs(redttl))  / redpaduration))),
                         "ttnpa": r.ttl(redkey) % redpaduration,
                         "ttl":   redttl}

            bluekey   = f'blue:{creature.id}'
            bluettl   = r.ttl(bluekey)
            blue = {"pa":    int(round(((bluemaxttl - abs(bluettl))  / bluepaduration))),
                         "ttnpa": r.ttl(bluekey) % bluepaduration,
                         "ttl":   bluettl}

            all  = {"red":  red,
                    "blue": blue}
        except Exception as e:
            logger.error(f'Method KO {e}')
            return None
        else:
            logger.trace(f'Method OK')
            return all

    @classmethod
    def reset(cls,creature):
        try:
            r.set(f'red:{creature.id}', 'red', ex=1)
            r.set(f'blue:{creature.id}','blue',ex=1)
        except Exception as e:
            logger.error(f'Method KO {e}')
            return None
        else:
            logger.trace(f'Method OK')
            return True
