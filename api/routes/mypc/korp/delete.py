# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Creature import CreatureDocument, CreatureKorp
from mongo.models.Korp import KorpDocument

from utils.decorators import (
    check_creature_exists,
    check_creature_in_korp,
    check_korp_exists,
    )
from utils.redis import cput, qput
from variables import PS_BROADCAST, YQ_DISCORD


# API: DELETE ../korp/<uuid:korpuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
@check_creature_in_korp
def korp_delete(creatureuuid, korpuuid):
    if g.Creature.korp.rank != 'Leader':
        msg = f'{g.h} Not the korp Leader ({g.Creature.korp.rank})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if CreatureDocument.objects(korp__id=g.Creature.korp.id).count() > 1:
        msg = f'{g.h} Korp not empty'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        KorpDocument.objects(_id=g.Korp.id).delete()
        g.Creature.korp = CreatureKorp()
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
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

    # Everything went well
    # Broadcast Channel
    cput(PS_BROADCAST, {
        "ciphered": False,
        "payload": g.Korp.to_json(),
        "route": 'mypc/{id1}/korp',
        "scope": 'korp'})
    # Discord Queue
    qput(YQ_DISCORD, {
        "ciphered": False,
        "payload": (
            f':information_source: **{g.Creature.name}** '
            f'deleted this Korp (**{g.Korp.name}**)'
            ),
        "embed": None,
        "scope": f'Korp-{g.Korp.id}'})

    msg = f'{g.h} Korp delete OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": None,
        }
    ), 200
