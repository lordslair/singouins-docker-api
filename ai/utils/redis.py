# -*- coding: utf8 -*-

import redis

from loguru import logger

from variables import REDIS_BASE, REDIS_HOST, REDIS_PORT

try:
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)
except Exception as e:
    logger.error(f'Redis Connection KO (r) [{e}]')
else:
    logger.debug('Redis Connection OK (r)')
