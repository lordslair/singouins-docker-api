# -*- coding: utf8 -*-

import yarqueue

from .connector import *

#
# Queries: Queues
#

def yqueue_put(yqueue_name,msg):
    # Opening Queue
    try:
        yqueue = yarqueue.Queue(name=yqueue_name, redis=r)
    except Exception as e:
        logger.error(f'Queue Connection KO (queue:{yqueue_name}) [{e}]')
    else:
        pass

    # Put data in Queue
    try:
        yqueue.put(json.dumps(msg))
    except Exception as e:
        logger.error(f'Queue Query KO (queue:{yqueue_name},msg:<{msg}>) [{e}]')
    else:
        pass

def yqueue_get(yqueue_name):
    # Opening Queue
    try:
        yqueue = yarqueue.Queue(name=yqueue_name, redis=r_no_decode)
    except Exception as e:
        logger.error(f'Queue Connection KO (queue:{yqueue_name}) [{e}]')
    else:
        pass

    # Get data from Queue
    try:
        msgs = []
        for msg in yqueue:
            msgs.append(json.loads(msg))
    except Exception as e:
        logger.error(f'Queue Query KO (queue:{yqueue_name}) [{e}]')
    else:
        return msgs
