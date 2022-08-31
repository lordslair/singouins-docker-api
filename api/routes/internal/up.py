# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from loguru             import logger

from mysql.methods      import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: GET /internal/up
def up_get():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    return jsonify({"msg": f'UP and running', "success": True, "payload": None}), 200
