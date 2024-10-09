# -*- coding: utf8 -*-

import datetime
from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Creature import CreatureSquad
from utils.decorators import (
    check_creature_exists,
    check_creature_in_squad,
    check_squad_exists,
    )
from utils.redis import cput, qput
from variables import PS_BROADCAST, YQ_DISCORD


# API: POST ../squad/<uuid:squaduuid>/leave
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_leave(creatureuuid, squaduuid):
    if g.Creature.squad.rank == 'Leader':
        msg = f'{g.h} Leader cannot decline'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.squad = CreatureSquad()
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
    except Exception as e:
        msg = f'{g.h} Squad leave KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Everything went well
    # Broadcast Channel
    cput(PS_BROADCAST, {
        "ciphered": False,
        "payload": g.Squad.to_json(),
        "route": 'mypc/{id1}/squad',
        "scope": 'squad'})
    # Discord Queue
    qput(YQ_DISCORD, {
        "ciphered": False,
        "payload": f':information_source: **{g.Creature.name}** left this Squad',
        "embed": None,
        "scope": f'Squad-{g.Squad.id}'})

    msg = f'{g.h} Squad leave OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": g.Squad.to_mongo(),
        }
    ), 200