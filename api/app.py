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

if __name__ == '__main__':
    app.run()
