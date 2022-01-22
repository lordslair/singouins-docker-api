# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from mysql.utils        import redis

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/* subpath
def creature_cds():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:cds')
    (code, success, msg, payload) = internal_creature_cds(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effects(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    redis.incr_query_count('internal:creature:effects')
    (code, success, msg, payload) = internal_creature_effects(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effect_add(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    duration   = request.json.get('duration')
    effectname = request.json.get('effectname')
    sourceid   = request.json.get('sourceid')

    redis.incr_query_count('internal:creature:effect:add')
    (code, success, msg, payload) = internal_creature_effects_add(creatureid,duration,effectname,sourceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effect_del(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    redis.incr_query_count('internal:creature:effect:del')
    (code, success, msg, payload) = internal_creature_effects_del(effectid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

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

def creature_profile():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:profile')
    (code, success, msg, payload) = internal_creature_profile(creatureid)
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

def creature_statuses():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:statuses')
    (code, success, msg, payload) = internal_creature_statuses(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_wallet():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    redis.incr_query_count('internal:creature:wallet')
    (code, success, msg, payload) = internal_creature_wallet(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# /internal/discord/* subpath
def discord_associate():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    usermail     = request.json.get('usermail')

    redis.incr_query_count('internal:discord:associate')
    (code, success, msg, payload) = internal_user_discord_associate(discordname,usermail)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def discord_creature():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname = request.json.get('discordname')
    creatureid  = request.json.get('creatureid')

    redis.incr_query_count('internal:discord:creature')
    (code, success, msg, payload) = internal_discord_creature(creatureid,discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def discord_creatures():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    redis.incr_query_count('internal:discord:creatures')
    (code, success, msg, payload) = internal_discord_creatures(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def discord_user():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    redis.incr_query_count('internal:discord:user')
    (code, success, msg, payload) = internal_user_discord(discordname)
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
