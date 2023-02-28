# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSlots    import RedisSlots


#
# Routes /pc
#
# API: GET /pc/<uuid:creatureuuid>
@jwt_required()
def pc_get_one(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = '[Creature.id:None]'

    if not hasattr(Creature, 'id'):
        msg = f'{h} Creature Query KO - Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 404
    else:
        h = f'[Creature.id:{Creature.id}]'

    msg = f'{h} Creature Query OK'
    logger.trace(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": Creature.as_dict(),
        }
    ), 200


# API: GET /pc/{creatureuuid}/item
@jwt_required()
def pc_item_get_all(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = '[Creature.id:None]'

    if not hasattr(Creature, 'id'):
        msg = f'{h} Equipment Query KO - Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 404
    else:
        h = f'[Creature.id:{Creature.id}]'

    # Response skeleton
    metas = {
        "feet": {
            "metaid": None,
            "metatype": None,
        },
        "hands": {
            "metaid": None,
            "metatype": None
        },
        "head": {
            "metaid": None,
            "metatype": None
        },
        "holster": {
            "metaid": None,
            "metatype": None
        },
        "lefthand": {
            "metaid": None,
            "metatype": None
        },
        "righthand": {
            "metaid": None,
            "metatype": None
        },
        "shoulders": {
            "metaid": None,
            "metatype": None
        },
        "torso": {
            "metaid": None,
            "metatype": None
        },
        "legs": {
            "metaid": None,
            "metatype": None
        },
    }

    # Check to see if the request is for a Monster, and not a player.
    if Creature.account is None:
        msg = f'{h} Equipment Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "equipment": metas,
                    "cosmetic": [],
                    },
            }
        ), 200

    try:
        Slots = RedisSlots(creatureuuid=creatureuuid)

        # We publicly anounce the cosmetics owned by a PC
        Cosmetics = RedisSearch().cosmetic(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} Equipment Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    for slot in [
        'feet',
        'hands',
        'head',
        'holster',
        'lefthand',
        'legs',
        'righthand',
        'shoulders',
        'torso',
    ]:
        itemuuid = getattr(Slots, slot)
        if itemuuid is not None:
            try:
                Item = RedisItem(itemuuid=itemuuid)
                metas[slot]['metaid'] = Item.metaid
                metas[slot]['metatype'] = Item.metatype
            except Exception as e:
                msg = f'{h} Items Query KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
    # Gruik: We need to clean some shit for 2H weapons
    if metas['lefthand']['metaid'] == metas['righthand']['metaid']:
        metas['lefthand']['metaid'] = None
        metas['lefthand']['metatype'] = None

    msg = f'{h} Equipment Query OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "equipment": metas,
                "cosmetic": [
                    Cosmetic.as_dict() for Cosmetic in Cosmetics.results
                    ],
                },
        }
    ), 200


# API: GET /pc/<uuid:creatureuuid>/event
@jwt_required()
def pc_event_get_all(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = '[Creature.id:None]'

    if Creature is None or Creature is False:
        msg = f'{h} Event Query KO - Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 404
    else:
        h = f'[Creature.id:{Creature.id}]'

    try:
        Events = RedisSearch(maxpaging=100).event(
            query=(
                f"(@src:{Creature.id.replace('-', ' ')}) | "
                f"(@dst:{Creature.id.replace('-', ' ')})"
                )
            )
    except Exception as e:
        msg = f'{h} Event Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Event Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [
                    Event.as_dict() for Event in Events.results
                    ],
            }
        ), 200
