# -*- coding: utf8 -*-

import os
import redis

from loguru import logger

# Redis variables
REDIS_HOST = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)

try:
    r = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB_NAME,
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
        db=REDIS_DB_NAME,
        encoding='utf-8',
        )
except Exception as e:
    logger.error(f'Redis Connection KO (r_no_decode) [{e}]')
else:
    logger.debug('Redis Connection OK (r_no_decode)')
