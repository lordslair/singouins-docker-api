# -*- coding: utf8 -*-

import json
import re
import redis

from loguru    import logger

from variables import (REDIS_PORT,
                       REDIS_HOST,
                       REDIS_DB_NAME)

r = redis.StrictRedis(host             = REDIS_HOST,
                      port             = REDIS_PORT,
                      db               = REDIS_DB_NAME,
                      encoding         = 'utf-8',
                      decode_responses = True)
