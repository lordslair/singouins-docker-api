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

from queries            import (query_get_user, query_add_user, query_del_user, query_set_user_confirmed,
                                query_get_pc,   query_add_pc,   query_del_pc,   query_get_pcs,
                                query_get_mp,   query_add_mp,   query_del_mp,   query_get_mps,
                                query_get_items)
from variables          import SEP_SECRET_KEY, SEP_URL, SEP_SHA

app = Flask(__name__)
CORS(app)                        # We wrap around all the app the CORS
metrics = PrometheusMetrics(app) # We wrap around all the app the metrics

# static information as metric
metrics.info('singouins_info', 'Application info', version='0.0.1', commit=SEP_SHA[0:7])

# Setup the flask_swagger_ui extension
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    '/swagger',
    '/static/swagger.yaml',
    config = { 'app_name': "S&P Internal API" }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/swagger')

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = SEP_SECRET_KEY
jwt = JWTManager(app)

# Auth route to send the JWT Token
@app.route('/auth/login', methods=['POST'])
def post_auth_login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if query_get_user(username):
        pass_db    = query_get_user(username).hash
        pass_check = check_password_hash(pass_db, password)
    else:
        pass_check = None

    if not query_get_user(username) or not pass_check:
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
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

# Auth route to register the user
@app.route('/auth/register', methods=['POST'])
def post_auth_register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    mail     = request.json.get('mail', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    if not mail:
        return jsonify({"msg": "Missing mail parameter"}), 400

    code = query_add_user(username,password,mail)
    if code == 201:
        from utils.mail import send
        from utils.token import generate_confirmation_token

        subject = '[🐒&🐖] Bienvenue {} !'.format(username)
        token   = generate_confirmation_token(mail)
        url     = SEP_URL + '/auth/confirm/' + token
        body    = 'Bienvenue parmi nous. Voici le lien de validation: ' + url
        if send(mail,subject,body):
            return jsonify({"msg": "User successfully added | mail OK"}), code
        else:
            return jsonify({"msg": "User successfully added | mail KO"}), 206
    elif code == 409:
        return jsonify({"msg": "User or Email already exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/auth/confirm/<string:token>', methods=['GET'])
def confirm_email(token):
    from utils.token import confirm_token

    if confirm_token(token):
        mail = confirm_token(token)
        code = query_set_user_confirmed(mail)
        if code == 201:
            return jsonify({"msg": "User successfully confirmed"}), code
        else:
            return jsonify({"msg": "Oops!"}), 422
    else:
        return jsonify({"msg": "Confirmation link invalid or has expired"}), 498

# Auth route to delete the user
@app.route('/auth/delete/<string:username>', methods=['DELETE'])
@jwt_required
def delete_auth_leave(username):
    current_user = get_jwt_identity()
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if username != current_user:
        return jsonify({"msg": "Token/username mismatch"}), 400

    code = query_del_user(username)
    if code == 200:
        return jsonify({"msg": "User successfully deleted"}), code
    if code == 404:
        return jsonify({"msg": "Bad username"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

# Info route when authenticated
@app.route('/auth/infos', methods=['GET'])
@jwt_required
def get_auth_infos():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

#
# Routes: /pc
#

@app.route('/mypc', methods=['POST'])
@jwt_required
def mypc_post():
    current_user = get_jwt_identity()
    pcname       = request.json.get('name', None)
    pcrace       = request.json.get('race', None)

    if not pcname or not pcrace:
        return jsonify({"msg": "Missing name/race parameter"}), 400

    code           = query_add_pc(current_user,pcname,pcrace)
    if code == 201:
        return jsonify({"msg": "PJ successfully created"}), code
    elif code == 409:
        return jsonify({"msg": "PJ already exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/pc/<int:pcid>', methods=['GET'])
@jwt_required
def pc_id_get(pcid):
    (code,pc) = query_get_pc(None,pcid)
    if code == 200:
        return jsonify(pc), code
    elif code == 404:
        return jsonify({"msg": "PJ does not exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/pc/name/<string:pcname>', methods=['GET'])
@jwt_required
def pc_name_get(pcname):
    (code,pc) = query_get_pc(pcname,None)
    if code == 200:
        return jsonify(pc), code
    elif code == 404:
        return jsonify({"msg": "PJ does not exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/mypc', methods=['GET'])
@jwt_required
def mypc_get():
    current_user = get_jwt_identity()
    (code,pcs)   = query_get_pcs(current_user)
    if code == 200:
        return jsonify(pcs), code
    elif code == 404:
        return jsonify({"msg": "PJ does not exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

@app.route('/mypc/<int:pcid>', methods=['GET'])
@jwt_required
def mypc_id_get(pcid):
    return jsonify({"msg": "Not yet implemented"}), 200

@app.route('/mypc/<int:pcid>', methods=['DELETE'])
@jwt_required
def mypc_delete(pcid):
    current_user = get_jwt_identity()
    code         = query_del_pc(current_user,pcid)
    if code == 200:
        return jsonify({"msg": "PJ successfully deleted"}), code
    elif code == 404:
        return jsonify({"msg": "PJ does not exists or does not belong to the token"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

#
# Routes: /mp
#

@app.route('/mypc/<int:pcid>/mp', methods=['POST'])
@jwt_required
def post_mp_send(pcid):
    (code,ret) = query_add_mp(get_jwt_identity(),
                              request.json.get('src', None),
                              request.json.get('dst', None),
                              request.json.get('subject', None),
                              request.json.get('body', None))
    if isinstance(code, int):
        return jsonify(ret), code

@app.route('/mypc/<int:pcid>/mp/<int:mpid>', methods=['GET'])
@jwt_required
def get_mp(pcid,mpid):
    (code,mp) = query_get_mp(get_jwt_identity(),pcid,mpid)
    if isinstance(code, int):
        return jsonify(mp), code

@app.route('/mypc/<int:pcid>/mp/<int:mpid>', methods=['DELETE'])
@jwt_required
def delete_mp(pcid,mpid):
    (code,ret) = query_del_mp(get_jwt_identity(),pcid,mpid)
    if isinstance(code, int):
        return jsonify(ret), code

@app.route('/mypc/<int:pcid>/mp', methods=['GET'])
@jwt_required
def get_mps(pcid):
    (code,mps) = query_get_mps(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify(mps), code

#
# Routes /item
#

@app.route('/mypc/<int:pcid>/item', methods=['GET'])
@jwt_required
def post_mp_send(pcid):
    (code,ret) = query_get_items(get_jwt_identity(),pcid)
    if isinstance(code, int):
        return jsonify(ret), code

if __name__ == '__main__':
    app.run()
