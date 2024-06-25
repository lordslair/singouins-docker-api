# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q

from mongo.models.Event import EventDocument

from utils.decorators import (
    check_creature_exists,
    )


#
# Routes /mypc/<uuid:creatureuuid>/event/*
#
# API: GET /mypc/<uuid:creatureuuid>/event
@jwt_required()
# Custom decorators
@check_creature_exists
def mypc_event_get_all(creatureuuid):
    try:
        query = Q(src=creatureuuid) | Q(dst=creatureuuid)
        Events = EventDocument.objects.filter(query)
    except Exception as e:
        msg = f'{g.h} Event Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Event Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [Event.to_mongo().to_dict() for Event in Events],
            }
        ), 200
