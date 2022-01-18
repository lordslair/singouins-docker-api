# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import (JWTManager,
                                jwt_required,
                                create_access_token,
                                create_refresh_token, jwt_refresh_token_required,
                                get_jwt_identity)
from flask_bcrypt       import check_password_hash
from flask_cors         import CORS
from flask_swagger_ui   import get_swaggerui_blueprint

from prometheus_flask_exporter import PrometheusMetrics

from werkzeug.middleware.proxy_fix import ProxyFix

from mysql.methods      import *
from mysql.utils        import redis
from variables          import (SEP_SECRET_KEY,
                                API_URL, DISCORD_URL,
                                LDP_HOST, LDP_TOKEN)
from utils.mail         import send
from utils.token        import generate_confirmation_token

# Imports of endpoint functions
import                  routes.admin
import                  routes.internal

# Imports only for LDP forwarding. Might be temporary
import logging
from marshmallow            import fields
from logging_ldp.formatters import LDPGELFFormatter
from logging_ldp.handlers   import LDPGELFTCPSocketHandler
from logging_ldp.schemas    import LDPSchema

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

# Auth route to send the JWT Token
@app.route('/auth/login', methods=['POST'])
def auth_login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if fn_user_get(username):
        pass_db    = fn_user_get(username).hash
        pass_check = check_password_hash(pass_db, password)
    else:
        pass_check = None

    if not fn_user_get(username) or not pass_check:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    ret = {
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200

# Auth route to refresh the token
@app.route('/auth/refresh', methods=['POST'])
@jwt_refresh_token_required
def auth_refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

# Auth route to register the user
@app.route('/auth/register', methods=['POST'])
def auth_register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    password = request.json.get('password', None)
    mail     = request.json.get('mail', None)
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    if not mail:
        return jsonify({"msg": "Missing mail parameter"}), 400

    code = add_user(mail,password)
    if code == 201:
        subject = '[🐒&🐖] Bienvenue chez le Singouins !'
        token   = generate_confirmation_token(mail)
        url     = API_URL + '/auth/confirm/' + token
        body    = open("/code/data/registered.html", "r").read()
        if send(mail,
                subject,
                body.format(urllogo    = '[INSERT LOGO HERE]',
                            urlconfirm = url,
                            urldiscord = DISCORD_URL)):
            return jsonify({"msg": "User successfully added | mail OK"}), code
        else:
            return jsonify({"msg": "User successfully added | mail KO"}), 206
    elif code == 409:
        return jsonify({"msg": "User or Email already exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/auth/confirm/<string:token>', methods=['GET'])
def auth_confirm(token):
    from utils.token import confirm_token

    if confirm_token(token):
        mail = confirm_token(token)
        code = set_user_confirmed(mail)
        if code == 201:
            return jsonify({"msg": "User successfully confirmed"}), code
        else:
            return jsonify({"msg": "Oops!"}), 422
    else:
        return jsonify({"msg": "Confirmation link invalid or has expired"}), 498

# Auth route to delete the user
@app.route('/auth/delete', methods=['DELETE'])
@jwt_required
def auth_delete():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username     = request.json.get('username', None)
    current_user = get_jwt_identity()

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if username != current_user:
        return jsonify({"msg": "Token/username mismatch"}), 400

    code = del_user(username)
    if code == 200:
        return jsonify({"msg": "User successfully deleted"}), code
    if code == 404:
        return jsonify({"msg": "Bad username"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/auth/forgotpassword', methods=['POST'])
def auth_forgotpassword():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    mail            = request.json.get('mail', None)
    (code,password) = forgot_password(mail)

    if code == 200:
        subject = '[🐒&🐖] Mot de passe oublié'
        token   = generate_confirmation_token(mail)
        url     = API_URL + '/auth/confirm/' + token
        body    = open("/code/data/forgot_password.html", "r").read()
        if send(mail,
                subject,
                body.format(urllogo    = '[INSERT LOGO HERE]',
                            password   = password,
                            urldiscord = DISCORD_URL)):
            return jsonify({"msg": "Password successfully replaced | mail OK"}), code
        else:
            return jsonify({"msg": "Password successfully replaced | mail KO"}), 206
    else:
        return jsonify({"msg": "Oops!"}), 422

# Info route when authenticated
@app.route('/auth/infos', methods=['GET'])
@jwt_required
def auth_infos():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

#
# Routes: /pc
#

@app.route('/pc/<int:pcid>', methods=['GET'])
@jwt_required
def api_pc_get(pcid):
    (code, success, msg, payload) = fn_creature_get(None,pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /mypc
#

@app.route('/mypc', methods=['POST'])
@jwt_required
def api_mypc_create():
    current_user = get_jwt_identity()
    pcclass      = request.json.get('class',     None)
    pccosmetic   = request.json.get('cosmetic',  None)
    pcequipment  = request.json.get('equipment', None)
    pcgender     = request.json.get('gender',    None)
    pcname       = request.json.get('name',      None)
    pcrace       = request.json.get('race',      None)

    (code, success, msg, payload) = mypc_create(current_user,
                                                pcname,pcrace,pcclass,
                                                pcequipment,pccosmetic,
                                                pcgender)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc', methods=['GET'])
@jwt_required
def api_mypc_get_all():
    current_user = get_jwt_identity()
    (code, success, msg, payload) = mypc_get_all(current_user)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>', methods=['GET'])
@jwt_required
def mypc_details(pcid):
    return jsonify({"msg": "Not yet implemented"}), 200

@app.route('/mypc/<int:pcid>', methods=['DELETE'])
@jwt_required
def api_mypc_del(pcid):
    current_user = get_jwt_identity()
    (code, success, msg, payload) = mypc_del(current_user,pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /pa
#

@app.route('/mypc/<int:pcid>/pa', methods=['GET'])
@jwt_required
def api_mypc_pa(pcid):
    (code, success, msg, payload) = redis.get_pa(pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /stats
#

@app.route('/mypc/<int:pcid>/stats', methods=['GET'])
@jwt_required
def api_mypc_stats_get(pcid):
    pc = fn_creature_get(None,pcid)[3]
    (code, success, msg, payload) = mypc_get_stats(pc)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /cds
#

@app.route('/mypc/<int:pcid>/cds', methods=['GET'])
@jwt_required
def api_mypc_cds_get(pcid):
    (code, success, msg, payload) = mypc_get_cds(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /effects
#

@app.route('/mypc/<int:pcid>/effects', methods=['GET'])
@jwt_required
def api_mypc_effects_get(pcid):
    (code, success, msg, payload) = mypc_get_effects(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /skills
#

@app.route('/mypc/<int:pcid>/skills', methods=['GET'])
@jwt_required
def api_mypc_skills_get(pcid):
    (code, success, msg, payload) = mypc_get_skills(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /view
#

@app.route('/mypc/<int:pcid>/view', methods=['GET'])
@jwt_required
def api_mypc_view(pcid):
    (code, success, msg, payload) = mypc_view(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /mp
#

@app.route('/mypc/<int:pcid>/mp', methods=['POST'])
@jwt_required
def api_mypc_mp_add(pcid):
    (code, success, msg, payload) = mypc_mp_add(get_jwt_identity(),
                                    request.json.get('src',     None),
                                    request.json.get('dst',     None),
                                    request.json.get('subject', None),
                                    request.json.get('body',    None))
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp/<int:mpid>', methods=['GET'])
@jwt_required
def api_mypc_mp_get(pcid,mpid):
    (code, success, msg, payload) = mypc_mp_get(get_jwt_identity(),pcid,mpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp/<int:mpid>', methods=['DELETE'])
@jwt_required
def api_mypc_mp_del(pcid,mpid):
    (code, success, msg, payload) = mypc_mp_del(get_jwt_identity(),pcid,mpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp', methods=['GET'])
@jwt_required
def api_mypc_mps_get(pcid):
    (code, success, msg, payload) = mypc_mps_get(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/mp/addressbook', methods=['GET'])
@jwt_required
def api_mypc_mp_addressbook(pcid):
    (code, success, msg, payload) = mypc_mp_addressbook(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": [{"id": row[0], "name": row[1]} for row in payload]}), code

#
# Routes /item
#

@app.route('/pc/<int:pcid>/item', methods=['GET'])
@jwt_required
def api_pc_item_get(pcid):
    (code, success, msg, payload) = pc_items_get(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/item', methods=['GET'])
@jwt_required
def api_mypc_item_get(pcid):
    (code, success, msg, payload) = mypc_items_get(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /inventory/item
#

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety>', methods=['POST'])
@jwt_required
def api_mypc_inventory_item_set_offset(pcid,itemid,offsetx,offsety):
    (code, success, msg, payload) = mypc_inventory_item_offset(get_jwt_identity(),pcid,itemid,offsetx,offsety)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/offset', methods=['DELETE'])
@jwt_required
def api_mypc_inventory_item_del_offset(pcid,itemid):
    (code, success, msg, payload) = mypc_inventory_item_offset(get_jwt_identity(),pcid,itemid,None,None)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname>', methods=['POST'])
@jwt_required
def api_mypc_inventory_item_equip(pcid,type,slotname,itemid):
    (code, success, msg, payload) = mypc_inventory_item_equip(get_jwt_identity(),pcid,type,slotname,itemid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname>', methods=['POST'])
@jwt_required
def api_mypc_inventory_item_unequip(pcid,type,slotname,itemid):
    (code, success, msg, payload) = mypc_inventory_item_unequip(get_jwt_identity(),pcid,type,slotname,itemid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle', methods=['POST'])
@jwt_required
def api_mypc_inventory_item_dismantle(pcid,itemid):
    (code, success, msg, payload) = mypc_inventory_item_dismantle(get_jwt_identity(),pcid,itemid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /trade
#

@app.route('/mypc/<int:pcid>/trade/item/<int:itemid>/give/<int:targetid>', methods=['POST'])
@jwt_required
def api_mypc_trade_item_give(pcid,itemid,targetid):
    (code, success, msg, payload) = mypc_trade_item_give(get_jwt_identity(),pcid,itemid,targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/trade/wallet/<string:currtype>/give/<int:targetid>/<int:amount>', methods=['POST'])
@jwt_required
def api_mypc_trade_wallet_give(pcid,currtype,targetid,amount):
    (code, success, msg, payload) = mypc_trade_wallet_give(get_jwt_identity(),pcid,currtype,targetid,amount)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /instance
#

@app.route('/mypc/<int:pcid>/instance', methods=['POST'])
@jwt_required
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

@app.route('/mypc/<int:pcid>/instance/<int:instanceid>/join', methods=['POST'])
@jwt_required
def api_mypc_instance_join(pcid,instanceid):
    (code, success, msg, payload) = mypc_instance_join(get_jwt_identity(),pcid,instanceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/instance/<int:instanceid>/leave', methods=['POST'])
@jwt_required
def api_mypc_instance_leave(pcid,instanceid):
    (code, success, msg, payload) = mypc_instance_leave(get_jwt_identity(),pcid,instanceid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /action
#

@app.route('/mypc/<int:pcid>/action/move', methods=['POST'])
@jwt_required
def api_mypc_action_move(pcid):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    path = request.json.get('path', None)
    (code, success, msg, payload) = mypc_action_move(get_jwt_identity(),pcid,path)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/attack/<int:weaponid>/<int:targetid>', methods=['POST'])
@jwt_required
def api_mypc_action_attack(pcid,weaponid,targetid):
    (code, success, msg, payload) = mypc_action_attack(get_jwt_identity(),pcid,weaponid,targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/reload/<int:weaponid>', methods=['POST'])
@jwt_required
def api_mypc_action_reload(pcid,weaponid):
    (code, success, msg, payload) = mypc_action_reload(get_jwt_identity(),pcid,weaponid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/action/unload/<int:weaponid>', methods=['POST'])
@jwt_required
def api_mypc_action_unload(pcid,weaponid):
    (code, success, msg, payload) = mypc_action_unload(get_jwt_identity(),pcid,weaponid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes: /events
#

@app.route('/mypc/<int:pcid>/event', methods=['GET'])
@jwt_required
def mypc_event(pcid):
    (code, success, msg, payload) = get_mypc_event(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/pc/<int:creatureid>/event', methods=['GET'])
@jwt_required
def pc_event(creatureid):
    (code, success, msg, payload) = get_pc_event(creatureid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /meta
#

@app.route('/meta/item/<string:itemtype>', methods=['GET'])
@jwt_required
def meta_item(itemtype):
    (code, success, msg, payload) = get_meta_item(itemtype)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /korp
#

@app.route('/mypc/<int:pcid>/korp/<int:korpid>', methods=['GET'])
@jwt_required
def api_mypc_korp_details(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_details(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp', methods=['POST'])
@jwt_required
def api_mypc_korp_create(pcid):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    (code, success, msg, payload) = mypc_korp_create(get_jwt_identity(),
                                                     pcid,
                                                     request.json.get('name'))
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>', methods=['DELETE'])
@jwt_required
def api_mypc_korp_delete(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_delete(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/invite/<int:targetid>', methods=['POST'])
@jwt_required
def api_mypc_korp_invite(pcid,korpid,targetid):
    (code, success, msg, payload) = mypc_korp_invite(get_jwt_identity(),
                                    pcid,
                                    korpid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/kick/<int:targetid>', methods=['POST'])
@jwt_required
def api_mypc_korp_kick(pcid,korpid,targetid):
    (code, success, msg, payload) = mypc_korp_kick(get_jwt_identity(),
                                    pcid,
                                    korpid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/accept', methods=['POST'])
@jwt_required
def api_mypc_korp_accept(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_accept(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/leave', methods=['POST'])
@jwt_required
def api_mypc_korp_leave(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_leave(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/korp/<int:korpid>/decline', methods=['POST'])
@jwt_required
def api_mypc_korp_decline(pcid,korpid):
    (code, success, msg, payload) = mypc_korp_decline(get_jwt_identity(),pcid,korpid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /squad
#

@app.route('/mypc/<int:pcid>/squad/<int:squadid>', methods=['GET'])
@jwt_required
def squad_details(pcid,squadid):
    (code, success, msg, payload) = get_squad(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad', methods=['POST'])
@jwt_required
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
@jwt_required
def squad_delete(pcid,squadid):
    (code, success, msg, payload) = del_squad(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/invite/<int:targetid>', methods=['POST'])
@jwt_required
def squad_invite(pcid,squadid,targetid):
    (code, success, msg, payload) = invite_squad_member(get_jwt_identity(),
                                    pcid,
                                    squadid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/kick/<int:targetid>', methods=['POST'])
@jwt_required
def squad_kick(pcid,squadid,targetid):
    (code, success, msg, payload) = kick_squad_member(get_jwt_identity(),
                                    pcid,
                                    squadid,
                                    targetid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/accept', methods=['POST'])
@jwt_required
def squad_accept(pcid,squadid):
    (code, success, msg, payload) = accept_squad_member(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/leave', methods=['POST'])
@jwt_required
def squad_leave(pcid,squadid):
    (code, success, msg, payload) = leave_squad_member(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

@app.route('/mypc/<int:pcid>/squad/<int:squadid>/decline', methods=['POST'])
@jwt_required
def squad_decline(pcid,squadid):
    (code, success, msg, payload) = decline_squad_member(get_jwt_identity(),pcid,squadid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /map
#

@app.route('/map/<int:mapid>', methods=['GET'])
@jwt_required
def map_get(mapid):
    (code, success, msg, payload) = get_map(mapid)
    if isinstance(code, int):
        return jsonify({"msg": msg, "success": success, "payload": payload}), code

#
# Routes /log
#

@app.route('/log', methods=['POST'])
def log_send():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "success": False, "payload": None}), 400

    log_level     = request.json.get('level',           None)
    log_msg_short = request.json.get('short_message',   None)

    # Load you config there
    config = dict(env     = request.json.get('_global_env',     None),
                  host    = request.json.get('_global_host',    None),
                  version = request.json.get('_global_version', None))

    # Define a custom Schema
    class MyApp(LDPSchema):
        global_env     = fields.Constant(config['env'])
        global_host    = fields.Constant(config['host'])
        global_version = fields.Constant(config['version'])

    handler = LDPGELFTCPSocketHandler(hostname=LDP_HOST)
    handler.setFormatter(LDPGELFFormatter(token=LDP_TOKEN, schema=MyApp))

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)

    try:
        if log_level == 1:
            logging.critical(log_msg_short)
        elif log_level == 2:
            logging.critical(log_msg_short)
        elif log_level == 3:
            logging.error(log_msg_short)
        elif log_level == 4:
            logging.warning(log_msg_short)
        elif log_level == 5:
            logging.warning(log_msg_short)
        elif log_level == 6:
            logging.info(log_msg_short)
        elif log_level == 7:
            logging.debug(log_msg_short)
    except Exception as e:
        # Something went wrong during query
        return jsonify({"msg": 'KO!', "success": False, "payload": e}), 200
    else:
        return jsonify({"msg": 'OK!', "success": True, "payload": None}), 200
    finally:
        logging.getLogger().removeHandler(handler)

#
# Routes /admin
#

app.add_url_rule('/admin/user',           methods=['POST'], view_func=routes.admin.user)
app.add_url_rule('/admin/user/validate',  methods=['POST'], view_func=routes.admin.user_validate)
app.add_url_rule('/admin/mypc',           methods=['POST'], view_func=routes.admin.mypc)
app.add_url_rule('/admin/mypc/effects',   methods=['POST'], view_func=routes.admin.mypc_effects)
app.add_url_rule('/admin/mypc/pa',        methods=['POST'], view_func=routes.admin.mypc_pa)
app.add_url_rule('/admin/mypc/equipment', methods=['POST'], view_func=routes.admin.mypc_equipment)
app.add_url_rule('/admin/mypc/statuses',  methods=['POST'], view_func=routes.admin.mypc_statuses)
app.add_url_rule('/admin/mypc/stats',     methods=['POST'], view_func=routes.admin.mypc_stats)
app.add_url_rule('/admin/mypc/wallet',    methods=['POST'], view_func=routes.admin.mypc_wallet)
app.add_url_rule('/admin/mypcs',          methods=['POST'], view_func=routes.admin.mypcs)

#
# Routes /internal
#
# Routes /internal/*
app.add_url_rule('/internal/korp',               methods=['POST'], view_func=routes.internal.korp)
app.add_url_rule('/internal/korps',              methods=['GET'],  view_func=routes.internal.korps)
app.add_url_rule('/internal/up',                 methods=['GET'],  view_func=routes.internal.up)
app.add_url_rule('/internal/squad',              methods=['POST'], view_func=routes.internal.squad)
app.add_url_rule('/internal/squads',             methods=['GET'],  view_func=routes.internal.squads)
# Routes /internal/creature/*
app.add_url_rule('/internal/creature/equipment', methods=['POST'], view_func=routes.internal.creature_equipment)
app.add_url_rule('/internal/creature/permission',methods=['POST'], view_func=routes.internal.creature_permission)
app.add_url_rule('/internal/creature/stats',     methods=['POST'], view_func=routes.internal.creature_stats)

if __name__ == '__main__':
    app.run()
