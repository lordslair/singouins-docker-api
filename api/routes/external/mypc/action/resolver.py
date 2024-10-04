# -*- coding: utf8 -*-

import json
import requests

from flask import g, jsonify, request
from flask_jwt_extended import jwt_required
from loguru import logger

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_is_json,
    )

from variables import RESOLVER_URL


#
# Routes /mypc/<uuid:creatureuuid>/action/resolver
#
# API: POST /mypc/<uuid:creatureuuid>/action/resolver
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
@check_creature_in_instance
def resolver(creatureuuid):
    try:
        json_for_resolver = request.json
        logger.trace(f'Received body: {json_for_resolver}')
        response = requests.post(f'{RESOLVER_URL}/', json=json_for_resolver)
    except Exception as e:
        msg = f'{g.h} Resolver Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if response:
        msg = f'{g.h} Resolver Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "resolver": json.loads(response.text),
                    "internal": json_for_resolver,
                    },
            }
        ), 200
    else:
        msg = f'{g.h} Resolver Query KO'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
