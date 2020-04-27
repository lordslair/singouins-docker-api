# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import (JWTManager,
                                jwt_required, create_access_token,
                                get_jwt_identity)
from flask_bcrypt       import check_password_hash

from queries            import query_get_user_exists, query_get_password
from variables          import SEP_SECRET_KEY, SEP_HEADER_TYPE

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = SEP_SECRET_KEY
app.config['JWT_HEADER_TYPE'] = SEP_HEADER_TYPE
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

    user_exists = query_get_user_exists(username)
    pass_db     = query_get_password(username)
    if pass_db:
        pass_check = check_password_hash(pass_db, password)
    else:
        pass_check = None

    if not user_exists or not pass_check:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

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

    code = query_set_pjauth(username,password,mail)
    if code == 201:
        from utils.mail import send
        subject = '[🐒&🐖] Bienvenue {} !'.format(username)
        body    = 'Bienvenue parmi nous'
        if send(mail,subject,body):
            return jsonify({"msg": "User successfully added | mail OK"}), code
        else:
            return jsonify({"msg": "User successfully added | mail KO"}), 206
    elif code == 409:
        return jsonify({"msg": "User already exists"}), code
    else:
        return jsonify({"msg": "Oops!"}), 422

# Info route when authenticated
@app.route('/auth/infos', methods=['GET'])
@jwt_required
def get_auth_infos():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run()
