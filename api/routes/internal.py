# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from mysql.utils.redis  import incr

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/* subpath
def creature_cd_add(creatureid,skillmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    duration    = request.json.get('duration')

    incr.one('queries:internal:creature:cd:add')
    (code, success, msg, payload) = internal_creature_cd_add(creatureid,duration,skillmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_cd_del(creatureid,skillmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:cd:del')
    (code, success, msg, payload) = internal_creature_cd_del(creatureid,skillmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_cd_get(creatureid,skillmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:cd:get')
    (code, success, msg, payload) = internal_creature_cd_get(creatureid,skillmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_cds(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:cd:get')
    (code, success, msg, payload) = internal_creature_cds(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effects(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:effect:get')
    (code, success, msg, payload) = internal_creature_effects(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effect_add(creatureid,effectmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    duration     = request.json.get('duration')
    sourceid     = request.json.get('sourceid')

    incr.one('queries:internal:creature:effect:add')
    (code, success, msg, payload) = internal_creature_effect_add(creatureid,duration,effectmetaid,sourceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effect_del(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:effect:del')
    (code, success, msg, payload) = internal_creature_effect_del(creatureid,effectid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_effect_get(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:effect:get')
    (code, success, msg, payload) = internal_creature_effect_get(creatureid,effectid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_equipment():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:equipment')
    (code, success, msg, payload) = internal_creature_equipment(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_pa():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:pa')
    (code, success, msg, payload) = internal_creature_pa(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_pa_reset():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:pa:reset')
    (code, success, msg, payload) = internal_creature_pa_reset(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_profile():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:profile')
    (code, success, msg, payload) = internal_creature_profile(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_stats():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:stats')
    (code, success, msg, payload) = internal_creature_stats(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_statuses():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:statuses')
    (code, success, msg, payload) = internal_creature_statuses(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creature_wallet():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    creatureid = request.json.get('creatureid')

    incr.one('queries:internal:creature:wallet')
    (code, success, msg, payload) = internal_creature_wallet(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def creatures_get():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creatures:get')
    (code, success, msg, payload) = internal_creatures_get()
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

    incr.one('queries:internal:discord:associate')
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

    incr.one('queries:internal:discord:creature')
    (code, success, msg, payload) = internal_discord_creature(creatureid,discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def discord_creatures():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    incr.one('queries:internal:discord:creatures')
    (code, success, msg, payload) = internal_discord_creatures(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def discord_user():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    incr.one('queries:internal:discord:user')
    (code, success, msg, payload) = internal_user_discord(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# /internal/* subpath
def korp():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    korpid  = request.json.get('korpid')

    incr.one('queries:internal:korp')
    (code, success, msg, payload) = internal_korp_get_one(korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korps():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:korps')
    (code, success, msg, payload) = internal_korp_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def squad():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    squadid      = request.json.get('squadid', None)

    incr.one('queries:internal:squad')
    (code, success, msg, payload) = internal_squad_get_one(squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def squads():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:squads')
    (code, success, msg, payload) = internal_squad_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def up():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:up')
    return jsonify({"msg": f'UP and running', "success": True, "payload": None}), 200
