# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request

from mysql.methods      import *

from variables          import API_ADMIN_TOKEN

#
# Routes /admin
#

def up():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    return jsonify({"msg": f'UP and running', "success": True, "payload": None}), 200

def user():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    (code, success, msg, payload) = admin_user(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def user_validate():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    usermail     = request.json.get('usermail')

    (code, success, msg, payload) = admin_user_validate(discordname,usermail)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def mypc():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    pcid         = request.json.get('pcid')

    (code, success, msg, payload) = admin_mypc_one(discordname,pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def mypcs():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')

    (code, success, msg, payload) = admin_mypc_all(discordname)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def squad():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    squadid      = request.json.get('squadid', None)

    if squadid is None:
        (code, success, msg, payload) = admin_squad_get_all()
        if isinstance(code, int):
            return jsonify({"msg": msg, "success": success, "payload": payload}), code
    elif isinstance(squadid, int):
        (code, success, msg, payload) = admin_squad_get_one(squadid)
        if isinstance(code, int):
            return jsonify({"msg": msg, "success": success, "payload": payload}), code
    else:
        return jsonify({"msg": f'Squad unknown (squadid:{squadid})', "success": False, "payload": None}), 200

def mypc_pa():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    pcid         = request.json.get('pcid')
    redpa        = request.json.get('redpa', None)
    bluepa       = request.json.get('bluepa', None)

    (code, success, msg, payload) = admin_mypc_pa(discordname,pcid,redpa,bluepa)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def mypc_wallet():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    pcid         = request.json.get('pcid')

    (code, success, msg, payload) = admin_mypc_wallet(discordname,pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code


def mypc_effects():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    pcid         = request.json.get('pcid')

    (code, success, msg, payload) = admin_mypc_effects(discordname,pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def mypc_statuses():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    discordname  = request.json.get('discordname')
    pcid         = request.json.get('pcid')

    (code, success, msg, payload) = admin_mypc_statuses(discordname,pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korp():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    korpid  = request.json.get('korpid')

    (code, success, msg, payload) = admin_korp_get_one(korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

def korps():
    if request.headers.get('Authorization') != f'Bearer {API_ADMIN_TOKEN}':
        return jsonify({"msg": 'Token not authorized', "success": False, "payload": None}), 403

    (code, success, msg, payload) = admin_korp_get_all()
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code
