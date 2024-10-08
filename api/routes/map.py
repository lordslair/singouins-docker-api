# -*- coding: utf8 -*-

from flask import jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Meta import MetaMap


#
# Routes /map
#
# API: GET /map/<int:map_id>
@jwt_required()
def map_get(map_id):
    try:
        Map = MetaMap.objects(_id=map_id)
    except MetaMap.DoesNotExist:
        msg = 'MetaMap Query KO (404)'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    except Exception as e:
        msg = f'Map query KO (map_id:{map_id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'Map query OK (map_id:{map_id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Map.get().to_mongo(),
            }
        ), 200
