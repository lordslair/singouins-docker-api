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
    key    = f'stats:{pc.id}:json'
    value  = json.dumps(stats)

    try:
        r.set(key,value,ttl)
    except Exception as e:
        print(f'set_stats failed:{e}')
        return False
    else:
        return True

def get_stats(pc):
    key    = f'stats:{pc.id}:json'

    try:
        if r.exists(key):
            # The pre-generated stats already exists in redis
            stats = json.loads(r.get(key))
        else:
            stats = None
    except Exception as e:
        print(f'get_stats failed:{e}')
        stats = None
    else:
        return stats

def get_hp(pc):
    key    = f'stats:{pc.id}:def:hp'

    try:
        if r.exists(key):
            hp = int(r.get(key).decode())
        else:
            hp = None
    except Exception as e:
        print(f'get_hp failed:{e}')
        hp = None
    else:
        return hp

def set_hp(pc,hp):
    key    = f'stats:{pc.id}:def:hp'

    try:
        r.set(key,hp)
    except Exception as e:
        print(f'set_hp failed:{e}')
        return False
    else:
        return True

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


def get_effects(pc):
    mypattern = f'effects:{pc.instance}:{pc.id}'
    effects   = []

    try:
        keys = r.scan_iter(mypattern + ':*:bearer')
    except Exception as e:
        print(f'scan_iter({mypattern}) failed:{e}')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+)", key.decode("utf-8"))
            if m:
                ts      = int(m.group(1))
                fullkey = mypattern + ':' + f'{ts}'
                ttl     = int(r.ttl(fullkey))
                effect  = {"bearer":          int(r.get(fullkey + ':bearer').decode("utf-8")),
                           "charge_base":     int(r.get(fullkey + ':charge_base').decode("utf-8")),
                           "charge_left":     int(r.get(fullkey + ':charge_left').decode("utf-8")),
                           "duration_base":   int(r.get(fullkey + ':duration_base').decode("utf-8")),
                           "duration_left":   ttl,
                           "timestamp_start": ts,
                           "timestamp_end":   ts - ttl,
                           "type":            r.get(fullkey + ':type').decode("utf-8")}
            effects.append(effect)
    except Exception as e:
        print(f'Effects fetching failed:{e}')
        return effects
    else:
        return effects

def get_statuses(pc):
    mypattern = f'statuses:{pc.instance}:{pc.id}'
    statuses  = []

    try:
        keys = r.scan_iter(mypattern + ':*:bearer')
    except Exception as e:
        print(f'scan_iter({mypattern}) failed:{e}')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+)", key.decode("utf-8"))
            if m:
                ts      = int(m.group(1))
                fullkey = mypattern + ':' + f'{ts}'
                ttl     = int(r.ttl(fullkey))
                status = {"bearer":          int(r.get(fullkey + ':bearer').decode("utf-8")),
                          "duration_base":   int(r.get(fullkey + ':duration_base').decode("utf-8")),
                          "duration_left":   ttl,
                          "timestamp_start": ts,
                          "timestamp_end":   ts - ttl,
                          "type":            r.get(fullkey + ':type').decode("utf-8")}
            statuses.append(status)
    except Exception as e:
        print(f'Statuses fetching failed:{e}')
        return statuses
    else:
        return statuses

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

def incr_query_count(route):
    increment = 1
    key       = f'queries:{route}'

    try:
        r.incr(key, amount=increment)
    except Exception as e:
        print(f'[Redis] incr_query_count({route}) failed [{e}]')
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
