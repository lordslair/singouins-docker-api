# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.publish              import publish

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature
def creature_add():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = '[Creature.id:None] Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    try:
        Creature = RedisCreature().new(
            None,
            request.json.get('raceid'),
            request.json.get('gender'),
            None,
            request.json.get('rarity'),
            request.json.get('x'),
            request.json.get('y'),
            request.json.get('instanceid')
            )
        h = f'[Creature.id:{Creature.id}]'  # Header for logging
    except Exception as e:
        msg = f'{h} Creature Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # We put the info in pubsub channel for IA to populate the instance
        try:
            pmsg     = {"action": 'pop',
                        "instance": None,
                        "creature": Creature._asdict()}
            pchannel = 'ai-creature'
            publish(pchannel, jsonify(pmsg).get_data())
        except Exception as e:
            msg = f'{h} Publish({pchannel}) KO [{e}]'
            logger.error(msg)
        else:
            logger.trace(f'{h} Publish({pchannel}) OK')

        msg = f'{h} Creature creation OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature._asdict(),
            }
        ), 201


# API: DELETE /internal/creature/{creatureid}
def creature_del(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    # We put the info in pubsub channel for IA to regulate the instance
    try:
        pmsg     = {"action": 'kill',
                    "instance": None,
                    "creature": Creature._asdict()}
        pchannel = 'ai-creature'
        publish(pchannel, jsonify(pmsg).get_data())
    except Exception as e:
        msg = f'{h} Publish({pchannel}) KO [{e}]'
        logger.error(msg)
    else:
        logger.trace(f'{h} Publish({pchannel}) OK')

    try:
        # Now we can delete tue PC itself
        RedisCreature().destroy(Creature.id)
    except Exception as e:
        msg = f'{h} Creature delete KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Creature delete OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200


# API: GET /internal/creature/{creatureid}
def creature_get_one(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging
        msg = f'{h} Creature Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature._asdict(),
            }
        ), 200


# API: GET /internal/creatures
def creature_get_all():
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = '[Creature.id:None] Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    try:
        # We search for ALL the Creature in an Instance
        Creatures = RedisCreature().search(query='-(@instance:None)')
    except Exception as e:
        msg = f'Creatures Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        msg = 'Creatures Query OK'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": Creatures}), 200
