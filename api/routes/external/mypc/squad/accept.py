# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Creature import CreatureSquad

from nosql.queue import yqueue_put

from utils.decorators import (
    check_creature_exists,
    check_creature_in_squad,
    check_squad_exists,
    )

from variables import YQ_BROADCAST, YQ_DISCORD


# API: POST /mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>/accept
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_accept(creatureuuid, squaduuid):
    if g.Creature.squad.rank != 'Pending':
        msg = f'{g.h} Pending is required'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.squad = CreatureSquad(
            id=g.Squad.id,
            rank='Member',
        )
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
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
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": g.Squad.to_json(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: **{g.Creature.name}** '
                    f'joined this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Squad.id}',
                }
            )
        msg = f'{g.h} Squad accept OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Squad.to_mongo(),
            }
        ), 200
