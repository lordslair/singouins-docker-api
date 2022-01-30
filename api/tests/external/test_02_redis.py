# -*- coding: utf8 -*-

import os
import redis
import sys
import time

r = redis.StrictRedis(host     = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST'],
                      port     = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT'],
                      db       = os.environ['SEP_REDIS_DB'],
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
