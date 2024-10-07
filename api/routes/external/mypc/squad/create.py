# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Creature import CreatureSquad
from mongo.models.Squad import SquadDocument

from utils.decorators import check_creature_exists
from utils.redis import qput
from variables import YQ_DISCORD


# API: POST ../squad
@jwt_required()
# Custom decorators
@check_creature_exists
def squad_create(creatureuuid):
    if g.Creature.squad.id is not None:
        msg = f'{g.h} Already in a Squad'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        if SquadDocument.objects(leader=g.Creature.id):
            Squad = SquadDocument.objects(leader=g.Creature.id).get()
            msg = f'{g.h} Squad Query KO - Already exists'
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": Squad.to_mongo(),
                }
            ), 409
        else:
            newSquad = SquadDocument(
                leader=g.Creature.id,
                )
            newSquad.save()
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

    # Squad created, let's assign the team creator in the squad
    try:
        g.Creature.squad = CreatureSquad(
            id=newSquad.id,
            rank='Leader'
            )
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
    except Exception as e:
        msg = f'{g.h} Squad Query KO (squaduuid:{newSquad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Everything went well
    # Discord Queue
    qput(YQ_DISCORD, {
        "ciphered": False,
        "payload": f':information_source: **{g.Creature.name}** created this Squad',
        "embed": None,
        "scope": f'Squad-{newSquad.id}'})

    msg = f'{g.h} Squad create OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": newSquad.to_mongo(),
        }
    ), 201
