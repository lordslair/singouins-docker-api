# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from nosql              import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/creature/*
# API: PUT /internal/creature
def creature_add():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    raceid     = request.json.get('raceid')
    gender     = request.json.get('gender')
    rarity     = request.json.get('rarity')
    instanceid = request.json.get('instanceid')
    x          = request.json.get('x')
    y          = request.json.get('y')
    m          = request.json.get('m')
    r          = request.json.get('r')
    g          = request.json.get('g')
    v          = request.json.get('v')
    p          = request.json.get('p')
    b          = request.json.get('b')

    (code, success, msg, payload) = internal_creature_add(raceid,gender,rarity,
                                                          instanceid,
                                                          x,y,
                                                          m,r,g,v,p,b)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: DELETE /internal/creature/{creatureid}
def creature_del(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    (code, success, msg, payload) = internal_creature_del(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: PUT /internal/creature/{creatureid}/cd/{skillmetaid}
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

# API: DELETE /internal/creature/{creatureid}/cd/{skillmetaid}
def creature_cd_del(creatureid,skillmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:cd:del')
    (code, success, msg, payload) = internal_creature_cd_del(creatureid,skillmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/{creatureid}/cd/{skillmetaid}
def creature_cd_get_one(creatureid,skillmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:cd:get')
    (code, success, msg, payload) = internal_creature_cd_get(creatureid,skillmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/{creatureid}/cds
def creature_cd_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:cd:get')
    (code, success, msg, payload) = internal_creature_cds(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/{creatureid}/effects
def creature_effect_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:effect:get')
    (code, success, msg, payload) = internal_creature_effects(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: PUT /internal/creature/{creatureid}/effect/{effectmetaid}
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

# API: DELETE /internal/creature/{creatureid}/effect/{effectid}
def creature_effect_del(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:effect:del')
    (code, success, msg, payload) = internal_creature_effect_del(creatureid,effectid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/{creatureid}/effect/{effectid}
def creature_effect_get_one(creatureid,effectid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:effect:get')
    (code, success, msg, payload) = internal_creature_effect_get(creatureid,effectid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/equipment
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

# API: GET /internal/creature/{creatureid}/pa
def creature_pa_get(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:pa:get')
    (code, success, msg, payload) = internal_creature_pa_get(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: PUT /internal/creature/{creatureid}/pa/consume/{redpa}/{bluepa}
def creature_pa_consume(creatureid,redpa,bluepa):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:pa:consume')
    (code, success, msg, payload) = internal_creature_pa_consume(creatureid,redpa,bluepa)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: POST /internal/creature/{creatureid}/pa/reset
def creature_pa_reset(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:pa:reset')
    (code, success, msg, payload) = internal_creature_pa_reset(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/profile
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

# API: GET /internal/creature/stats
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

# API: PUT /internal/creature/{creatureid}/status/{statusmetaid}
def creature_status_add(creatureid,statusmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    duration    = request.json.get('duration')

    incr.one('queries:internal:creature:status:add')
    (code, success, msg, payload) = internal_creature_status_add(creatureid,duration,statusmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: DELETE /internal/creature/{creatureid}/status/{statusmetaid}
def creature_status_del(creatureid,statusmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:status:del')
    (code, success, msg, payload) = internal_creature_status_del(creatureid,statusmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: GET /internal/creature/{creatureid}/status/{statusmetaid}
def creature_status_get_one(creatureid,statusmetaid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:status:get')
    (code, success, msg, payload) = internal_creature_status_get(creatureid,statusmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: PUT /internal/creature/{creatureid}/statuses/{effectmetaid}
def creature_status_get_all(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creature:status:get')
    (code, success, msg, payload) = internal_creature_statuses(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# API: PUT /internal/creature/wallet
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

# API: GET /internal/creatures
def creature_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    incr.one('queries:internal:creatures:get')
    (code, success, msg, payload) = internal_creatures_get()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
