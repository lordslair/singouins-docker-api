# -*- coding: utf8 -*-

from .connector import *

def many(key,increment):

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
