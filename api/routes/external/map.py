# -*- coding: utf8 -*-

from flask              import Flask, jsonify, request
from flask_jwt_extended import jwt_required

from nosql              import *

#
# Routes /map
#
# API: GET /map/{mapid}
@jwt_required()
def map_get(mapid):
    # Pre-flight checks
    if not isinstance(mapid, int):
        return jsonify({"success": False,
                        "msg": f'Map ID should be an integer (mapid:{mapid})',
                        "payload": None}), 200
    try:
        map = maps.get_map(mapid)
    except Exception as e:
        return jsonify({"success": False,
                        "msg": f'[Redis:get_map()] Map query KO (mapid:{mapid})',
                        "payload": None}), 200
    else:
        if map:
            return jsonify({"success": True,
                            "msg": f'[Redis:get_map()] Map query OK (mapid:{mapid})',
                            "payload": map}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Map not found (mapid:{mapid})',
                            "payload": None}), 200
