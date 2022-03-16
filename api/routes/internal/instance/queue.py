# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from nosql              import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: GET /internal/instance/queue
def queue_get():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:instance:queue')

    try:
        msgs = queue.yqueue_get('yarqueue:instances')
    except Exception as e:
        msg = f'Queue Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = f'Queue Query OK'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": msgs}), 200
