# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *
from nosql              import *

from variables          import API_INTERNAL_TOKEN

#
# Routes /internal
#
# /internal/discord/*
# /internal/discord/associate
def discord_associate():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    usermail     = request.json.get('usermail')

    incr.one('queries:internal:discord:associate')
    (code, success, msg, payload) = internal_discord_user_associate(discordname,usermail)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# /internal/discord/creature
def discord_creature_get_one():
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

# /internal/discord/creatures
def discord_creature_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    incr.one('queries:internal:discord:creatures')
    (code, success, msg, payload) = internal_discord_creatures(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

# /internal/discord/user
def discord_user():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    incr.one('queries:internal:discord:user')
    (code, success, msg, payload) = internal_discord_user(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
