# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger

from mongo.models.Creature import CreatureDocument

from utils.decorators import check_user_exists


# API: GET /mypc
@jwt_required()
# Custom decorators
@check_user_exists
def mypc_get_all():
    g.h = f'[User.id:{g.User.id}]'
    try:
        Creatures = CreatureDocument.objects(account=g.User.id)
    except Exception as e:
        msg = f'{g.h} Creatures query KO (username:{get_jwt_identity()}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Creatures Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [Creature.to_mongo() for Creature in Creatures],
            }
        ), 200
