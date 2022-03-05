#!/usr/bin/env python3
# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import (JWTManager,
                                jwt_required,
                                get_jwt_identity)
from flask_cors         import CORS
from flask_swagger_ui   import get_swaggerui_blueprint

from prometheus_flask_exporter import PrometheusMetrics

from werkzeug.middleware.proxy_fix import ProxyFix

# Import Redis and initialize
import                      nosql

from mysql.methods          import *

# Imports of endpoint functions
import                      routes.internal.creature
import                      routes.internal.discord
import                      routes.internal.korp
import                      routes.internal.instance.queue
import                      routes.internal.meta
import                      routes.internal.squad
import                      routes.internal.up

import                      routes.external.auth
import                      routes.external.log
import                      routes.external.map
import                      routes.external.meta
import                      routes.external.mypc
import                      routes.external.mypc.events
import                      routes.external.pc

from variables              import *
from utils.gunilog          import *

app = Flask(__name__)
CORS(app)                        # We wrap around all the app the CORS
metrics = PrometheusMetrics(app) # We wrap around all the app the metrics

# Setup the flask_swagger_ui extension
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    '/swagger',
    '/static/swagger.yaml',
    config = { 'app_name': "S&P Internal API" }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/swagger')

# Setup the ProxyFix to have the Real-IP in the logs
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = SEP_SECRET_KEY
jwt = JWTManager(app)

#
# Routes /check (k8s livenessProbe)
#
@app.route('/check', methods=['GET'])
def check():
    return jsonify({"msg": f'UP and running',
                    "success": True,
                    "payload": None}), 200

#
# Routes /auth
#
app.add_url_rule('/auth/confirm/<string:token>',
                 methods=['GET'],
                 view_func=routes.external.auth.auth_confirm)
app.add_url_rule('/auth/delete',
                 methods=['DELETE'],
                 view_func=routes.external.auth.auth_delete)
app.add_url_rule('/auth/forgotpassword',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_forgotpassword)
app.add_url_rule('/auth/infos',
                 methods=['GET'],
                 view_func=routes.external.auth.auth_infos)
app.add_url_rule('/auth/login',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_login)
app.add_url_rule('/auth/refresh',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_refresh)
app.add_url_rule('/auth/register',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_register)
#
# Routes /meta
#
app.add_url_rule('/meta/item/<string:metatype>',
                 methods=['GET'],
                 view_func=routes.external.meta.external_meta_get_one)
#
# Routes: /pc
#
app.add_url_rule('/pc/<int:creatureid>',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_get_one)

app.add_url_rule('/pc/<int:creatureid>/item',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_item_get_all)

app.add_url_rule('/pc/<int:creatureid>/event',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_event_get_all)
#
# Routes: /mypc
#
app.add_url_rule('/mypc',
                 methods=['POST'],
                 view_func=routes.external.mypc.mypc_add)
app.add_url_rule('/mypc',
                 methods=['GET'],
                 view_func=routes.external.mypc.mypc_get_all)
app.add_url_rule('/mypc/<int:pcid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.mypc_del)

#
# Routes: /pa
#

@app.route('/mypc/<int:pcid>/pa', methods=['GET'])
@jwt_required()
def api_mypc_pa(pcid):
    (code, success, msg, payload) = pa.get_pa(pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /stats
#

@app.route('/mypc/<int:pcid>/stats', methods=['GET'])
@jwt_required()
def api_mypc_stats_get(pcid):
    pc = fn_creature_get(None,pcid)[3]
    (code, success, msg, payload) = mypc_get_stats(pc)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /cds
#

@app.route('/mypc/<int:pcid>/cds', methods=['GET'])
@jwt_required()
def api_mypc_cds_get(pcid):
    (code, success, msg, payload) = mypc_get_cds(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /effects
#

@app.route('/mypc/<int:pcid>/effects', methods=['GET'])
@jwt_required()
def api_mypc_effects_get(pcid):
    (code, success, msg, payload) = mypc_get_effects(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code


#
# Routes: /view
#

@app.route('/mypc/<int:pcid>/view', methods=['GET'])
@jwt_required()
def api_mypc_view(pcid):
    (code, success, msg, payload) = mypc_view(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /mp
#

@app.route('/mypc/<int:pcid>/mp', methods=['POST'])
@jwt_required()
def api_mypc_mp_add(pcid):
    (code, success, msg, payload) = mypc_mp_add(get_jwt_identity(),
                                    request.json.get('src',     None),
                                    request.json.get('dst',     None),
                                    request.json.get('subject', None),
                                    request.json.get('body',    None))
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp/<int:mpid>', methods=['GET'])
@jwt_required()
def api_mypc_mp_get(pcid,mpid):
    (code, success, msg, payload) = mypc_mp_get(get_jwt_identity(),pcid,mpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp/<int:mpid>', methods=['DELETE'])
@jwt_required()
def api_mypc_mp_del(pcid,mpid):
    (code, success, msg, payload) = mypc_mp_del(get_jwt_identity(),pcid,mpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp', methods=['GET'])
@jwt_required()
def api_mypc_mps_get(pcid):
    (code, success, msg, payload) = mypc_mps_get(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp/addressbook', methods=['GET'])
@jwt_required()
def api_mypc_mp_addressbook(pcid):
    (code, success, msg, payload) = mypc_mp_addressbook(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": [{"id": row[0], "name": row[1]} for row in payload]}), code

#
# Routes /item
#



@app.route('/mypc/<int:pcid>/item', methods=['GET'])
@jwt_required()
def api_mypc_item_get(pcid):
    (code, success, msg, payload) = mypc_items_get(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /inventory/item
#

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety>', methods=['POST'])
@jwt_required()
def api_mypc_inventory_item_set_offset(pcid,itemid,offsetx,offsety):
    (code, success, msg, payload) = mypc_inventory_item_offset(get_jwt_identity(),pcid,itemid,offsetx,offsety)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/offset', methods=['DELETE'])
@jwt_required()
def api_mypc_inventory_item_del_offset(pcid,itemid):
    (code, success, msg, payload) = mypc_inventory_item_offset(get_jwt_identity(),pcid,itemid,None,None)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname>', methods=['POST'])
@jwt_required()
def api_mypc_inventory_item_equip(pcid,type,slotname,itemid):
    (code, success, msg, payload) = mypc_inventory_item_equip(get_jwt_identity(),pcid,type,slotname,itemid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname>', methods=['POST'])
@jwt_required()
def api_mypc_inventory_item_unequip(pcid,type,slotname,itemid):
    (code, success, msg, payload) = mypc_inventory_item_unequip(get_jwt_identity(),pcid,type,slotname,itemid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle', methods=['POST'])
@jwt_required()
def api_mypc_inventory_item_dismantle(pcid,itemid):
    (code, success, msg, payload) = mypc_inventory_item_dismantle(get_jwt_identity(),pcid,itemid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /trade
#

@app.route('/mypc/<int:pcid>/trade/item/<int:itemid>/give/<int:targetid>', methods=['POST'])
@jwt_required()
def api_mypc_trade_item_give(pcid,itemid,targetid):
    (code, success, msg, payload) = mypc_trade_item_give(get_jwt_identity(),pcid,itemid,targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/trade/wallet/<string:currtype>/give/<int:targetid>/<int:amount>', methods=['POST'])
@jwt_required()
def api_mypc_trade_wallet_give(pcid,currtype,targetid,amount):
    (code, success, msg, payload) = mypc_trade_wallet_give(get_jwt_identity(),pcid,currtype,targetid,amount)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /instance
#

@app.route('/mypc/<int:pcid>/instance', methods=['PUT'])
@jwt_required()
def api_mypc_instance_create(pcid):
    (code, success, msg, payload) = mypc_instance_create(
                                        get_jwt_identity(),
                                        pcid,
                                        request.json.get('hardcore', None),
                                        request.json.get('fast',     None),
                                        request.json.get('mapid',    None),
                                        request.json.get('public',   None))
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/instance/<int:instanceid>', methods=['GET'])
@jwt_required()
def api_mypc_instance_get(pcid,instanceid):
    (code, success, msg, payload) = mypc_instance_get(get_jwt_identity(),pcid,instanceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/instance/<int:instanceid>/join', methods=['POST'])
@jwt_required()
def api_mypc_instance_join(pcid,instanceid):
    (code, success, msg, payload) = mypc_instance_join(get_jwt_identity(),pcid,instanceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/instance/<int:instanceid>/leave', methods=['POST'])
@jwt_required()
def api_mypc_instance_leave(pcid,instanceid):
    (code, success, msg, payload) = mypc_instance_leave(get_jwt_identity(),pcid,instanceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /action
#

@app.route('/mypc/<int:pcid>/action/resolver/move', methods=['POST'])
@jwt_required()
def api_mypc_action_resolver_move(pcid):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    path = request.json.get('path', None)
    (code, success, msg, payload) = mypc_action_resolver_move(get_jwt_identity(),pcid,path)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/resolver/skill/<int:skillmetaid>', methods=['PUT'])
@jwt_required()
def api_mypc_action_resolver_skill(pcid,skillmetaid):

    (code, success, msg, payload) = mypc_action_resolver_skill(get_jwt_identity(),
                                                               pcid,
                                                               skillmetaid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
#
#

@app.route('/mypc/<int:pcid>/action/move', methods=['POST'])
@jwt_required()
def api_mypc_action_move(pcid):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    path = request.json.get('path', None)
    (code, success, msg, payload) = mypc_action_move(get_jwt_identity(),pcid,path)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/attack/<int:weaponid>/<int:targetid>', methods=['POST'])
@jwt_required()
def api_mypc_action_attack(pcid,weaponid,targetid):
    (code, success, msg, payload) = mypc_action_attack(get_jwt_identity(),pcid,weaponid,targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/reload/<int:weaponid>', methods=['POST'])
@jwt_required()
def api_mypc_action_reload(pcid,weaponid):
    (code, success, msg, payload) = mypc_action_reload(get_jwt_identity(),pcid,weaponid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/unload/<int:weaponid>', methods=['POST'])
@jwt_required()
def api_mypc_action_unload(pcid,weaponid):
    (code, success, msg, payload) = mypc_action_unload(get_jwt_identity(),pcid,weaponid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /events
#
app.add_url_rule('/mypc/<int:creatureid>/event',
                 methods=['GET'],
                 view_func=routes.external.mypc.events.mypc_event_get_all)

#
# Routes /korp
#

@app.route('/mypc/<int:pcid>/korp/<int:korpid>', methods=['GET'])
@jwt_required()
def api_mypc_korp_details(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_details(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp', methods=['POST'])
@jwt_required()
def api_mypc_korp_create(pcid):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    (code, success, msg, payload) = mypc_korp_create(get_jwt_identity(),
                                                     pcid,
                                                     request.json.get('name'))
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>', methods=['DELETE'])
@jwt_required()
def api_mypc_korp_delete(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_delete(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/invite/<int:targetid>', methods=['POST'])
@jwt_required()
def api_mypc_korp_invite(pcid,korpid,targetid):
    (code, success, msg, payload) = mypc_korp_invite(get_jwt_identity(),
                                    pcid,
                                    korpid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/kick/<int:targetid>', methods=['POST'])
@jwt_required()
def api_mypc_korp_kick(pcid,korpid,targetid):
    (code, success, msg, payload) = mypc_korp_kick(get_jwt_identity(),
                                    pcid,
                                    korpid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/accept', methods=['POST'])
@jwt_required()
def api_mypc_korp_accept(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_accept(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/leave', methods=['POST'])
@jwt_required()
def api_mypc_korp_leave(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_leave(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/decline', methods=['POST'])
@jwt_required()
def api_mypc_korp_decline(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_decline(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /squad
#

@app.route('/mypc/<int:pcid>/squad/<int:squadid>', methods=['GET'])
@jwt_required()
def squad_details(pcid,squadid):
    (code, success, msg, payload) = get_squad(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad', methods=['POST'])
@jwt_required()
def squad_create(pcid):
    # Unicity test commented before release:alpha. Meditation needed
    #if not request.is_json:
    #    return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400
    (code, success, msg, payload) = add_squad(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>', methods=['DELETE'])
@jwt_required()
def squad_delete(pcid,squadid):
    (code, success, msg, payload) = del_squad(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/invite/<int:targetid>', methods=['POST'])
@jwt_required()
def squad_invite(pcid,squadid,targetid):
    (code, success, msg, payload) = invite_squad_member(get_jwt_identity(),
                                    pcid,
                                    squadid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/kick/<int:targetid>', methods=['POST'])
@jwt_required()
def squad_kick(pcid,squadid,targetid):
    (code, success, msg, payload) = kick_squad_member(get_jwt_identity(),
                                    pcid,
                                    squadid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/accept', methods=['POST'])
@jwt_required()
def squad_accept(pcid,squadid):
    (code, success, msg, payload) = accept_squad_member(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/leave', methods=['POST'])
@jwt_required()
def squad_leave(pcid,squadid):
    (code, success, msg, payload) = leave_squad_member(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/decline', methods=['POST'])
@jwt_required()
def squad_decline(pcid,squadid):
    (code, success, msg, payload) = decline_squad_member(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /map
#
app.add_url_rule('/map/<int:mapid>',
                 methods=['GET'],
                 view_func=routes.external.map.map_get)
#
# Routes /log
#
app.add_url_rule('/log',
                 methods=['POST'],
                 view_func=routes.external.log.front)
#
# Routes /internal
#
# Routes /internal/*
app.add_url_rule('/internal/korp',
                 methods=['POST'],
                 view_func=routes.internal.korp.korp_get_one)
app.add_url_rule('/internal/korps',
                 methods=['GET'],
                 view_func=routes.internal.korp.korp_get_all)
#
app.add_url_rule('/internal/meta/<string:metatype>',
                 methods=['GET'],
                 view_func=routes.internal.meta.internal_meta_get_one)
#
app.add_url_rule('/internal/squad',
                 methods=['POST'],
                 view_func=routes.internal.squad.squad_get_one)
app.add_url_rule('/internal/squads',
                 methods=['GET'],
                 view_func=routes.internal.squad.squad_get_all)
#
app.add_url_rule('/internal/up',
                 methods=['GET'],
                 view_func=routes.internal.up.up_get)
# Routes /internal/creature/*
app.add_url_rule('/internal/creature',
                 methods=['PUT'],
                 view_func=routes.internal.creature.creature_add)
app.add_url_rule('/internal/creature/equipment',
                 methods=['POST'],
                 view_func=routes.internal.creature.creature_equipment)
app.add_url_rule('/internal/creature/profile',
                 methods=['POST'],
                 view_func=routes.internal.creature.creature_profile)
app.add_url_rule('/internal/creature/stats',
                 methods=['POST'],
                 view_func=routes.internal.creature.creature_stats)
app.add_url_rule('/internal/creature/wallet',
                 methods=['POST'],
                 view_func=routes.internal.creature.creature_wallet)
# Routes /internal/creature/{creatureid}
app.add_url_rule('/internal/creature/<int:creatureid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.creature_del)
# Routes /internal/creature/{creatureid}/cd/*
app.add_url_rule('/internal/creature/<int:creatureid>/cd/<int:skillmetaid>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.creature_cd_add)
app.add_url_rule('/internal/creature/<int:creatureid>/cd/<int:skillmetaid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.creature_cd_del)
app.add_url_rule('/internal/creature/<int:creatureid>/cd/<int:skillmetaid>',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_cd_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>/cds',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_cd_get_all)
# Routes /internal/creature/{creatureid}/effect/*
app.add_url_rule('/internal/creature/<int:creatureid>/effect/<int:effectmetaid>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.creature_effect_add)
app.add_url_rule('/internal/creature/<int:creatureid>/effect/<int:effectid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.creature_effect_del)
app.add_url_rule('/internal/creature/<int:creatureid>/effect/<int:effectid>',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_effect_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>/effects',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_effect_get_all)
# Routes /internal/creature/{creatureid}/pa/*
app.add_url_rule('/internal/creature/<int:creatureid>/pa',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_pa_get)
app.add_url_rule('/internal/creature/<int:creatureid>/pa/consume/<int:redpa>/<int:bluepa>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.creature_pa_consume)
app.add_url_rule('/internal/creature/<int:creatureid>/pa/reset',
                 methods=['POST'],
                 view_func=routes.internal.creature.creature_pa_reset)
# Routes /internal/creature/{creatureid}/status/*
app.add_url_rule('/internal/creature/<int:creatureid>/status/<int:statusmetaid>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.creature_status_add)
app.add_url_rule('/internal/creature/<int:creatureid>/status/<int:statusmetaid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.creature_status_del)
app.add_url_rule('/internal/creature/<int:creatureid>/status/<int:statusmetaid>',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_status_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>/statuses',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_status_get_all)
# Routes /internal/creatures/*
app.add_url_rule('/internal/creatures',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_get_all)
# Routes /internal/discord/*
app.add_url_rule('/internal/discord/associate',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_associate)
app.add_url_rule('/internal/discord/creature',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_creature_get_one)
app.add_url_rule('/internal/discord/creatures',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_creature_get_all)
app.add_url_rule('/internal/discord/user',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_user)
# Routes /internal/instance/*
app.add_url_rule('/internal/instance/queue',
                 methods=['GET'],
                 view_func=routes.internal.instance.queue.queue_get)

if __name__ == '__main__':
    intercept_handler = InterceptHandler()
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout}])

    options = {
        "bind":         GUNICORN_BIND,
        "workers":      GUNICORN_WORKERS,
        "threads":      GUNICORN_THREADS,
        "accesslog":    "-",
        "errorlog":     "-",
        "logger_class": StubbedGunicornLogger,
        "reload":       GUNICORN_RELOAD,
        "chdir":        GUNICORN_CHDIR
    }

    StandaloneApplication(app, options).run()
