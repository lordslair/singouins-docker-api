# -*- coding: utf8 -*-

from datetime                   import datetime

from ..engine                   import engine
from ..base                     import Base

from .redis.connector           import r
from .redis.variables           import META_FILES

def initialize_db():
    print('DB init: start')

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f'DB init: failed [{e}]')
    else:
        print('DB init: done')

    print('DB init: end')

def initialize_redis():
    print(f'Redis init: start')

    try:
        r.set('system:startup',datetime.now().isoformat())

    except Exception as e:
        print(f'Redis init: failed [{e}]')
    else:
        print('Redis init: created system:startup')

    try:
        for meta,file in META_FILES.items():
            with open(file) as f:
                content = f.read()
                print(f'Redis init: creating system:meta:{meta}')
                r.set(f'system:meta:{meta}', content)
    except Exception as e:
        print(f'Redis init: failed [{e}]')
    else:
        print(f'Redis init: created system:meta:*')

    print('Redis init: end')
