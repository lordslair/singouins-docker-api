# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.metas                import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats    import RedisStats
from nosql.publish              import publish

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    request_json_check,
    )

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature
def creature_add():
    h = '[Creature.id:None]'
    request_internal_token_check(request)
    request_json_check(request)

    try:
        # We create first the Creature (It will be a monster)
        try:
            Creature = RedisCreature().new(
                metaNames['race'][request.json.get('raceid')]['name'],
                request.json.get('raceid'),
                request.json.get('gender'),
                None,
                request.json.get('rarity'),
                request.json.get('x'),
                request.json.get('y'),
                request.json.get('instanceid')
                )
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
            h = f'[Creature.id:{Creature.id}]'  # Header for logging

        # We add the minimum informations we need in Redis
        try:
            Stats = RedisStats(Creature).new(classid=None)
        except Exception as e:
            msg = f'{h} Stats Query KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.trace(f'{h} Stats Query OK')
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
            pmsg = {
                "action": 'pop',
                "instance": None,
                "creature": Creature._asdict(),
                "stats": Stats._asdict(),
                }
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
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    # We put the info in pubsub channel for IA to regulate the instance
    try:
        pmsg     = {"action": 'kill',
                    "instance": Creature.instance,
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
        RedisStats(Creature).destroy()
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
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

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
    request_internal_token_check(request)

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
