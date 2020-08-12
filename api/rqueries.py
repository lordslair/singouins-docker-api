# -*- coding: utf8 -*-

import redis

from datetime  import datetime

from variables import (REDIS_PORT,
                       REDIS_HOST,
                       REDIS_DB_NAME)

r = redis.StrictRedis(host     = REDIS_HOST,
                      port     = REDIS_PORT,
                      db       = REDIS_DB_NAME,
                      encoding = 'utf-8')

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

#
# Queries: PA
#

def rget_pa(pcid):

    redkey    = str(pcid) + '-red'
    redttl    = r.ttl(redkey)
    redpa     = int(round(((redmaxttl - abs(redttl))  / redpaduration)))
    redttnpa  = r.ttl(redkey) % redpaduration

    bluekey   = str(pcid) + '-blue'
    bluettl   = r.ttl(bluekey)
    bluepa    = int(round(((bluemaxttl - abs(bluettl))  / bluepaduration)))
    bluettnpa = r.ttl(bluekey) % bluepaduration

    return (200, True, 'OK', {"red": {"pa": redpa, "ttnpa": redttnpa, "ttl": redttl},
                              "blue": {"pa": bluepa, "ttnpa": bluettnpa, "ttl": bluettl}})
