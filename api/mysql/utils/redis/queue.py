# -*- coding: utf8 -*-

import json
import yarqueue

from .connector import r

#
# Queries: Queues
#

def yqueue_put(yqueue_name,msg):
    # Opening Queue
    try:
        yqueue      = yarqueue.Queue(name=yqueue_name, redis=r)
    except:
        print(f'Connection to yarqueue:{yqueue_name} [✗]')
    else:
        pass

    # Put data in Queue
    try:
        yqueue.put(json.dumps(msg))
    except:
        print(f'yarqueue:{yqueue_name} <{msg}> [✗]')
    else:
        pass

def yqueue_get(yqueue_name):
    # Opening Queue
    try:
        yqueue = yarqueue.Queue(name=yqueue_name, redis=r)
    except:
        print(f'Connection to yarqueue:{yqueue_name} [✗]')
    else:
        pass

    # Get data from Queue
    try:
        msgs = []
        for msg in yqueue:
            msgs.append(json.loads(msg))
    except:
        print(f'Failed to get messages from yarqueue:{yqueue_name} [✗]')
    else:
        return msgs
