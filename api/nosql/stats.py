# -*- coding: utf8 -*-

from .connector import *

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
            hp = int(r.get(key))
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
