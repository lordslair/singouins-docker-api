# -*- coding: utf8 -*-

from loguru import logger

from nosql.connector import r

try:
    config = r.config_get(pattern='notify-keyspace-events')
    if 'notify-keyspace-events' not in config or config['notify-keyspace-events'] == '':
        r.config_set(name='notify-keyspace-events', value='$sxE')
        logger.debug('Redis init: notify-keyspace-events OK')
except Exception as e:
    logger.error(f'Redis init: notify-keyspace-events KO [{e}]')
