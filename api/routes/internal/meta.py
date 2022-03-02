# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from nosql              import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: GET /internal/meta
def meta_get_one(metatype):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:meta')
    (code, success, msg, payload) = internal_meta_get_one(metatype)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
