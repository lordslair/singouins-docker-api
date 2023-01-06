# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r

#
# Queries: Redis.publish
#


def publish(channel, msg):
    # Opening Queue
    try:
        r.publish(channel, msg)
    except Exception as e:
        logger.error(f'Publish({channel}) KO [{e}]')
        return None
    else:
        logger.trace(f'Publish({channel}) OK')
        return True
