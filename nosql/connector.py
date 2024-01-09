# -*- coding: utf8 -*-

import os
import redis

from loguru import logger

# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_BASE = os.environ.get("REDIS_BASE", 0)

try:
    r = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_BASE,
        encoding='utf-8',
        decode_responses=True,
        )
except Exception as e:
    logger.error(f'Redis Connection KO (r) [{e}]')
else:
    logger.debug('Redis Connection OK (r)')


# Used only for yarque.get() at is does not handle pre-decoded responses
try:
    r_no_decode = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_BASE,
        encoding='utf-8',
        )
except Exception as e:
    logger.error(f'Redis Connection KO (r_no_decode) [{e}]')
else:
    logger.debug('Redis Connection OK (r_no_decode)')
