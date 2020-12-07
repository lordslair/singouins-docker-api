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

def get_pa(pc):

    redkey    = str(pc.id) + '-red'
    redttl    = r.ttl(redkey)
    redpa     = int(round(((redmaxttl - abs(redttl))  / redpaduration)))
    redttnpa  = r.ttl(redkey) % redpaduration
    redbar    = redpa*'🟥' + (redpamax-redpa)*'⬜'

    bluekey   = str(pc.id) + '-blue'
    bluettl   = r.ttl(bluekey)
    bluepa    = int(round(((bluemaxttl - abs(bluettl))  / bluepaduration)))
    bluettnpa = r.ttl(bluekey) % bluepaduration
    bluebar   = bluepa*'🟦' + (bluepamax-bluepa)*'⬜'

    rettext   = f'Creature : [{pc.id}] {pc.name}\n'
    rettext  += f'PA blue  : {bluebar}\n'
    rettext  += f'PA red   : {redbar}\n'
    return (f'```{rettext}```')

def reset_pa(pc,blue,red):

    if red:
        r.set(str(pc.id) + '-red','red',ex=1)
    if blue:
        r.set(str(pc.id) + '-blue','blue',ex=1)
