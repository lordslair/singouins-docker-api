# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q

from mongo.models.Creature import CreatureDocument

from utils.decorators import (
    check_creature_exists,
    check_creature_in_korp,
    check_korp_exists,
    )


# API: GET ../korp/<uuid:korpuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
@check_creature_in_korp
def korp_get(creatureuuid, korpuuid):
    try:
        query_members = (
            Q(korp__id=g.Korp.id) &
            Q(korp__rank__ne="Pending")
            )
        KorpMembers = CreatureDocument.objects.filter(query_members)

        query_pending = (
            Q(korp__id=g.Korp.id) &
            Q(korp__rank="Pending")
            )
        KorpPendings = CreatureDocument.objects.filter(query_pending)
    except Exception as e:
        msg = f'{g.h} Korp Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Korp Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "members": [KorpMember.to_mongo() for KorpMember in KorpMembers],
                    "pending": [KorpPending.to_mongo() for KorpPending in KorpPendings],
                    "korp": g.Korp.to_mongo(),
                    }
            }
        ), 200
