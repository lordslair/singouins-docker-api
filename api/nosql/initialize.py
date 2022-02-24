# -*- coding: utf8 -*-

from datetime             import datetime
from loguru               import logger

from .connector            import r
from .variables            import META_FILES

def initialize_redis():
    try:
        logger.info(f'Redis init: start')
        r.set('system:startup',datetime.now().isoformat())
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:startup')

    try:
        for meta,file in META_FILES.items():
            with open(file) as f:
                content = f.read()
                logger.debug(f'Redis init: creating system:meta:{meta}')
                r.set(f'system:meta:{meta}', content)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info(f'Redis init: OK system:meta:*')
    finally:
        logger.info('Redis init: end')
