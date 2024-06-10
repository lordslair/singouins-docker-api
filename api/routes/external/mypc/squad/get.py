# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q

from mongo.models.Creature import CreatureDocument

from utils.decorators import (
    check_creature_exists,
    check_creature_in_squad,
    check_squad_exists,
    )


# API: GET ../squad/<uuid:squaduuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_get(creatureuuid, squaduuid):
    try:
        query_members = (
            Q(squad__id=g.Squad.id) &
            Q(squad__rank__ne="Pending")
            )
        SquadMembers = CreatureDocument.objects.filter(query_members)

        query_pending = (
            Q(squad__id=g.Squad.id) &
            Q(squad__rank="Pending")
            )
        SquadPendings = CreatureDocument.objects.filter(query_pending)
    except Exception as e:
        msg = f'{g.h} Squad Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Squad Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "members": [SquadMember.to_mongo() for SquadMember in SquadMembers],
                    "pending": [SquadPending.to_mongo() for SquadPending in SquadPendings],
                    "squad": g.Squad.to_mongo(),
                    }
            }
        ), 200
