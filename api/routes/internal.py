# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from mysql.utils        import redis

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

    redis.incr_query_count('internal:creature:equipment')
    (code, success, msg, payload) = internal_creature_equipment(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_pa():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:pa')
    (code, success, msg, payload) = internal_creature_pa(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_pa_reset():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:pa:reset')
    (code, success, msg, payload) = internal_creature_pa_reset(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_permission():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname = request.json.get('discordname')
    creatureid  = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:permission')
    (code, success, msg, payload) = internal_creature_permission(creatureid,discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_stats():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:stats')
    (code, success, msg, payload) = internal_creature_stats(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# /internal/* subpath
def up():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    redis.incr_query_count('internal:up')
    return jsonify({"msg": f'UP and running', "success": True, "payload": None}), 200

def squad():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    squadid      = request.json.get('squadid', None)

    redis.incr_query_count('internal:squad')
    (code, success, msg, payload) = internal_squad_get_one(squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def squads():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    redis.incr_query_count('internal:squads')
    (code, success, msg, payload) = internal_squad_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korp():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    korpid  = request.json.get('korpid')

    redis.incr_query_count('internal:korp')
    (code, success, msg, payload) = internal_korp_get_one(korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korps():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    redis.incr_query_count('internal:korps')
    (code, success, msg, payload) = internal_korp_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
