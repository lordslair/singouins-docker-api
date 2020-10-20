# -*- coding: utf8 -*-

import os
import redis
import sys
import time

code = os.path.dirname(os.environ['FLASK_APP'])
sys.path.append(code)

from variables import (REDIS_PORT, REDIS_HOST, REDIS_DB_NAME)

r = redis.StrictRedis(host     = REDIS_HOST,
                      port     = REDIS_PORT,
                      db       = REDIS_DB_NAME,
                      encoding = 'utf-8')

def test_singouins_redis_connection():
    assert r.ping()

def test_singouins_redis_set():
    assert r.set('test_singouins', 'OK', ex = 1)

def test_singouins_redis_get():
    assert r.get('test_singouins')

def test_singouins_redis_expired():
    time.sleep(1)
    assert not r.get('test_singouins')
