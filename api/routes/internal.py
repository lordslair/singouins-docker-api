# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/* subpath
def creature_equipment():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    (code, success, msg, payload) = internal_creature_equipment(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# /internal/* subpath
def up():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    return jsonify({"msg": f'UP and running', "success": True, "payload": None}), 200

def squad():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    squadid      = request.json.get('squadid', None)

    (code, success, msg, payload) = internal_squad_get_one(squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def squads():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    (code, success, msg, payload) = internal_squad_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korp():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    korpid  = request.json.get('korpid')

    (code, success, msg, payload) = internal_korp_get_one(korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korps():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    (code, success, msg, payload) = internal_korp_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
