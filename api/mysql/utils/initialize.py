# -*- coding: utf8 -*-

from datetime                   import datetime

from ..engine                   import engine
from ..base                     import Base

from .redis                     import *

def initialize_db():
    print('DB init: start')
    Base.metadata.create_all(bind=engine)
    print('DB init: end')

def initialize_redis():
    print('Redis init: start')
    try:
        r.set('system:startup',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print(f'Redis init: failed {e}')
    print('Redis init: end')
