# -*- coding: utf8 -*-

import datetime

from flask import g, jsonify, request
from flask_jwt_extended import jwt_required
from loguru import logger

from nosql.queue import yqueue_put

from mongo.models.Creature import CreatureKorp
from mongo.models.Korp import KorpDocument

from utils.decorators import (
    check_creature_exists,
    check_is_json,
    )

from variables import YQ_BROADCAST, YQ_DISCORD


# API: POST ../korp
@jwt_required()
# Custom decorators
@check_is_json
@check_creature_exists
def korp_create(creatureuuid):
    korpname = request.json.get('name', None)

    if g.Creature.korp.id is not None:
        msg = f'{g.h} Already in a Korp'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        if KorpDocument.objects(name=korpname):
            msg = f'{g.h} Korp Query KO - Already exists'
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": KorpDocument.objects(name=korpname).to_mongo(),
                }
            ), 409
        else:
            newKorp = KorpDocument(
                leader=g.Creature.id,
                name=korpname,
                )
            newKorp.save()
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

    # Korp created, let's assign the team creator in the korp
    try:
        g.Creature.korp = CreatureKorp(
            id=newKorp.id,
            rank='Leader'
            )
        g.Creature.updated = datetime.datetime.utcnow()
        g.Creature.save()
    except Exception as e:
        msg = f'{g.h} Korp Query KO (korpuuid:{newKorp.id}) [{e}]'
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
                "payload": newKorp.to_json(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'created this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{newKorp.id}',
                }
            )

        msg = f'{g.h} Korp create OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": newKorp.to_mongo(),
            }
        ), 201
