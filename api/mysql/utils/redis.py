# -*- coding: utf8 -*-

import json
import re
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

def set_stats(pc,stats):
    ttl    = 300
    key    = f'stats:{pc.id}'
    value  = json.dumps(stats)

    try:
        r.set(key,value,ttl)
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
            stats = None
    except Exception as e:
        stats = None
    else:
        return stats

#
# Queries: Creature CDs/States/Effects
#

def set_cd(pc,skillid,pa):
    ttl    = pa * redpaduration
    key    = f'cds:{pc.instance}:{pc.id}:{skillid}'
    value  = ''

    try:
        r.set(key,value,ttl)
    except Exception as e:
        print(f'set_cd failed:{e}')
        return False
    else:
        return True

def get_cds(pc):
    cds       = {}
    mypattern = f'cds:{pc.instance}:{pc.id}:*'

    try:
        mylua = """
        local keys = redis.call('keys', '%s')
    local result = {}
    for i,k in ipairs(keys) do
        local ttl = redis.call('ttl', k)
        result[i] = {ttl}
    end
    return result
        """ % (mypattern) # Gruik but difficult to format a HereDoc
        mttl = r.register_script(mylua)

        keys   = r.keys(pattern=mypattern)
        ttls   = mttl()
    except Exception as e:
        print(e)
    else:
        for key,ttl in zip(keys,ttls):
            m = re.search(r":(?P<skillid>\d+)$", key.decode("utf-8"))
            if m is not None:
                cds[m.group('skillid')] = ttl[0]
        return cds

#
# Queries: Creature High Scores
#

def incr_hs(pc,path,increment):

    key    = f'highscores:{pc.id}:{path}'

    try:
        r.incr(key, amount=increment)
    except Exception as e:
        print(f'incr_hs failed:{e}')
        return False
    else:
        return True

#
# Queries: Queues
#

def yqueue_put(yqueue_name,msg):
    # Opening Queue
    try:
        yqueue      = yarqueue.Queue(name=yqueue_name, redis=r)
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
