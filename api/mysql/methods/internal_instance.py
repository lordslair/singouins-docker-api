# -*- coding: utf8 -*-

from nosql import * # Custom internal module for Redis queries

#
# Queries /internal/creature/*
#
# API: Get /internal/instance/queue
def internal_instance_queue_get():

    try:
        msgs = queue.yqueue_get('yarqueue:instances')
    except Exception as e:
        return (200,
                False,
                f'[Redis:yqueue_get()] Query failed [{e}]',
                None)
    else:
        return (200,
                True,
                f'Instance queue query successed',
                msgs)
