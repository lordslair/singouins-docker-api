# -*- coding: utf8 -*-

import json
import redis
import yarqueue

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


#
# Queries: Creature Stats
#

def set_stats(pc):
    ttl    = 300
    key    = f'stats:{pc.id}'
    value  = {"base":{"m": pc.m,
                      "r": pc.r,
                      "g": pc.g,
                      "v": pc.v,
                      "p": pc.p,
                      "b": pc.b},
             "off":{"capcom": round((pc.g + round((pc.m + pc.r)/2))/2),
                    "capsho": round((pc.v + round((pc.b + pc.r)/2))/2)},
             "def":{"hpmax": 100 + pc.m + round(pc.level/2),
                    "dodge": pc.r,
                    "parry": round((pc.g-100)/50) * round((pc.m-100)/50)}}
    try:
        r.set(key,json.dumps(value),ttl)
    except Exception as e:
        print(f'set_stats failed:{e}')
        return False
    else:
        return True

def get_stats(pc):
    key    = f'stats:{pc.id}'

    try:
        if r.exists(key):
            # The pre-generated stats already exists in redis
            stats = json.loads(r.get(key))
        else:
            set_stats(pc)
            stats = json.loads(r.get(key))
    except Exception as e:
        return (200,
                False,
                f'[Redis] Stats query failed (pcid:{pc.id})',
                None)
    else:
        return (200,
                True,
                f'Stats query Successed (pcid:{pc.id})',
                stats)

#
# Queries: Queues
#

qr = redis.StrictRedis(host     = REDIS_HOST,
                       port     = REDIS_PORT,
                       db       = REDIS_DB_NAME,
                       encoding = 'utf-8')

def yqueue_put(yqueue_name,msg):
    # Opening Queue
    try:
        yqueue      = yarqueue.Queue(name=yqueue_name, redis=qr)
    except:
        print(f'Connection to yarqueue:{yqueue_name} [✗]')
    else:
        pass

    # Put data in Queue
    try:
        yqueue.put(json.dumps(msg))
    except:
        print(f'yarqueue:{yqueue_name} <{msg}> [✗]')
    else:
        pass
