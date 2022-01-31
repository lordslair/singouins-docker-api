# -*- coding: utf8 -*-

from .connector import r

def many(key,increment):

    key    = f'highscores:{pc.id}:{path}'

    try:
        r.incr(key, amount=increment)
    except Exception as e:
        print(f'incr_hs failed:{e}')
        return False
    else:
        return True

def one(key):
    increment = 1

    try:
        r.incr(key, amount=increment)
    except Exception as e:
        print(f'[Redis] incr.({key}) failed [{e}]')
        return False
    else:
        return True