# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from nosql              import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# API: GET /internal/korp
def korp_get_one():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    korpid  = request.json.get('korpid')

    incr.one('queries:internal:korp')
    (code, success, msg, payload) = internal_korp_get_one(korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/korps
def korp_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:korps')
    (code, success, msg, payload) = internal_korp_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
