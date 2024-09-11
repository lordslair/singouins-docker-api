# -*- coding: utf8 -*-

import json
import yarqueue

from loguru import logger

from nosql.connector import r


def qput(queue, msg):
    """ Put a new message (dict) into a specified queue. """
    try:
        logger.trace(f'Queue PUT >> (queue:{queue})')
        yqueue = yarqueue.Queue(name=queue, redis=r)
        json_msg = json.dumps(msg)
        yqueue.put(json_msg)
    except Exception as e:
        logger.error(f'Queue PUT KO (queue:{queue}) [{e}]')
    else:
        logger.trace(f'Queue PUT OK (queue:{queue})')
