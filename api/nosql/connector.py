# -*- coding: utf8 -*-

import json
import re
import redis

from loguru    import logger

from variables import (REDIS_PORT,
                       REDIS_HOST,
                       REDIS_DB_NAME)

try:
    r = redis.StrictRedis(host             = REDIS_HOST,
                          port             = REDIS_PORT,
                          db               = REDIS_DB_NAME,
                          encoding         = 'utf-8',
                          decode_responses = True)
except Exception as e:
    logger.error(f'Redis Connection KO (r) [{e}]')
else:
    logger.debug(f'Redis Connection OK (r)')


# Used only for yarque.get() at is does not handle pre-decoded responses
try:
    r_no_decode = redis.StrictRedis(host     = REDIS_HOST,
                                    port     = REDIS_PORT,
                                    db       = REDIS_DB_NAME,
                                    encoding = 'utf-8')
except Exception as e:
    logger.error(f'Redis Connection KO (r_no_decode) [{e}]')
else:
    logger.debug(f'Redis Connection OK (r_no_decode)')
