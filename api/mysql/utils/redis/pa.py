# -*- coding: utf8 -*-

from .connector import r

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

#
# Queries: red:*
#          blue:*
#

def get_pa(pcid):

    redkey    = f'red:{pcid}'
    redttl    = r.ttl(redkey)
    redpa     = int(round(((redmaxttl - abs(redttl))  / redpaduration)))
    redttnpa  = r.ttl(redkey) % redpaduration

    bluekey   = f'blue:{pcid}'
    bluettl   = r.ttl(bluekey)
    bluepa    = int(round(((bluemaxttl - abs(bluettl))  / bluepaduration)))
    bluettnpa = r.ttl(bluekey) % bluepaduration

    return (200, True, 'OK', {"red": {"pa": redpa, "ttnpa": redttnpa, "ttl": redttl},
                              "blue": {"pa": bluepa, "ttnpa": bluettnpa, "ttl": bluettl}})

def set_pa(pcid,redpa,bluepa):

    if bluepa > 0:
        # An action consumed a blue PA, we need to update
        key    = f'blue:{pcid}'
        ttl    = r.ttl(key)
        newttl = ttl + (bluepa * bluepaduration)

        if ttl > 0:
            # Key still exists (PA count < PA max)
            r.expire(key,newttl)
        else:
            # Key does not exist anymore (PA count = PA max)
            r.set(key,'blue',ex=newttl)
    if redpa > 0:
        # An action consumed a red PA, we need to update
        key    = f'red:{pcid}'
        ttl    = r.ttl(key)
        newttl = ttl + (redpa * redpaduration)

        if ttl > 0:
            # Key still exists (PA count < PA max)
            r.expire(key,newttl)
        else:
            # Key does not exist anymore (PA count = PA max)
            r.set(key,'red',ex=newttl)