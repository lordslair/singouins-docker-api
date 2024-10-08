# -*- coding: utf8 -*-

import redis

from loguru import logger

from variables import env_vars

try:
    r = redis.StrictRedis(
        host=env_vars['REDIS_HOST'],
        port=env_vars['REDIS_PORT'],
        db=env_vars['REDIS_BASE']
        )
except Exception as e:
    logger.error(f'Redis Connection KO (r) [{e}]')
else:
    logger.debug('Redis Connection OK (r)')
