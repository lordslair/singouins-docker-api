# -*- coding: utf8 -*-

from .connector import *

#
# Queries: Redis.publish
#

def publish(channel,msg):
    # Opening Queue
    try:
        r.publish(channel,msg)
    except Exception as e:
        logger.error(f'Publish({channel}) KO [{e}]')
        return None
    else:
        logger.trace(f'Publish({channel}) OK')
        return True
