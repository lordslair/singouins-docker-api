# -*- coding: utf8 -*-

from flask import jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine.connection import get_db


#
# Routes /meta
#
# API: GET /meta/item/<string:metatype>
@jwt_required()
def external_meta_get_one(metatype):

    try:
        # Get the database object
        db = get_db()
        # Access a collection by its name
        my_collection = db[f'_meta{metatype}s']
        results = list(my_collection.find())
    except Exception as e:
        msg = f'Query KO (metatype:{metatype}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'Meta Query OK (metatype:{metatype})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": results,
            }
        ), 200
