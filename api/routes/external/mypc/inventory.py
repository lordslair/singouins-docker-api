# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.metas                import metaNames
from nosql.queue                import yqueue_put
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisItem    import RedisItem
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    )

from variables                  import YQ_BROADCAST


#
# Routes /mypc/<uuid:creatureuuid>/inventory/*
#
# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/dismantle
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
def inventory_item_dismantle(creatureuuid, itemuuid):
    if RedisPa(creatureuuid=creatureuuid).bluepa < 1:
        msg = f'{g.h} Not enough PA'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        # We add the shards in the wallet
        Wallet = RedisWallet(creatureuuid=creatureuuid)
        if g.Item.rarity == 'Broken':
            wallet_value = getattr(Wallet, g.Item.rarity.lower())
            setattr(Wallet, g.Item.rarity.lower(), wallet_value + 6)
        elif g.Item.rarity == 'Common':
            wallet_value = getattr(Wallet, g.Item.rarity.lower())
            setattr(Wallet, g.Item.rarity.lower(), wallet_value + 5)
        elif g.Item.rarity == 'Uncommon':
            wallet_value = getattr(Wallet, g.Item.rarity.lower())
            setattr(Wallet, g.Item.rarity.lower(), wallet_value + 4)
        elif g.Item.rarity == 'Rare':
            wallet_value = getattr(Wallet, g.Item.rarity.lower())
            setattr(Wallet, g.Item.rarity.lower(), wallet_value + 3)
        elif g.Item.rarity == 'Epic':
            wallet_value = getattr(Wallet, g.Item.rarity.lower())
            setattr(Wallet, g.Item.rarity.lower(), wallet_value + 2)
        elif g.Item.rarity == 'Legendary':
            wallet_value = getattr(Wallet, g.Item.rarity.lower())
            setattr(Wallet, g.Item.rarity.lower(), wallet_value + 1)
    except Exception as e:
        msg = f'{g.h} Wallet/Shards Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        # We destroy the item
        g.Item.destroy()
    except Exception as e:
        msg = f'{g.h} Item({itemuuid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        # We consume the blue PA (1)
        RedisPa(creatureuuid=creatureuuid).consume(bluepa=1)
        # We add HighScore
        RedisHS(creatureuuid=creatureuuid).incr('action_dismantle')
    except Exception as e:
        msg = f'{g.h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Item({itemuuid}) Dismantle OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creature": g.Creature.as_dict(),
                    "wallet": Wallet.as_dict(),
                    },
            }
        ), 200


# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/equip/<string:type>/<string:slotname> # noqa
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
def inventory_item_equip(creatureuuid, type, slotname, itemuuid):
    try:
        Stats = RedisStats(creatureuuid=creatureuuid)
        Slots = RedisSlots(creatureuuid=creatureuuid)
    except Exception as e:
        msg = f'{g.h} Stats Query KO - failed [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    itemmeta = metaNames[type][g.Item.metaid]
    sizex, sizey = itemmeta['size'].split("x")
    costpa = round(int(sizex) * int(sizey) / 2)
    if RedisPa(creatureuuid=creatureuuid).redpa < costpa:
        msg = (
            f"{g.h} Not enough PA "
            f"(redpa:{RedisPa(creatureuuid=creatureuuid).redpa},cost:{costpa})"
            )
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-requisite checks
    for carac in ['m', 'r', 'g', 'v', 'p', 'b']:
        needed = itemmeta[f'min_{carac}']
        stat = getattr(Stats, carac)
        if needed > stat:
            msg = (
                f"{g.h} {carac.upper()} prequisites KO "
                f"(min_{carac}:{needed} > {carac}:{stat})"
                )
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    try:
        # The item to equip exists
        # is owned by the PC, and we retrieved his equipment from DB
        if slotname == 'holster':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the holster
                Slots.holster = g.Item.id
            else:
                msg = (f"{g.h} Item does not fit in holster "
                       f"(itemid:{g.Item.id},size:{itemmeta['size']})")
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        elif slotname == 'righthand':
            if Slots.righthand:
                # Something is already equipped in RH
                equipped = RedisItem(itemuuid=Slots.righthand)
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    equippedMeta = metaNames['weapon'][equipped.metaid]
                    if equippedMeta['onehanded'] is True:
                        # A 1H weapons is in RH : we replace
                        Slots.righthand = g.Item.id
                    if equippedMeta['onehanded'] is False:
                        # A 2H weapons is in RH & LH
                        # We replace RH and clean LH
                        Slots.righthand = g.Item.id
                        Slots.lefthand = None
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    Slots.righthand = g.Item.id
                    Slots.lefthand = g.Item.id
            else:
                # Nothing in RH
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    Slots.righthand = g.Item.id
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    Slots.righthand = g.Item.id
                    Slots.lefthand = g.Item.id
        elif slotname == 'lefthand':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the left hand
                Slots.lefthand = g.Item.id
            else:
                msg = (
                    f"{g.h} Item does not fit in left hand "
                    f"(itemid:{g.Item.id},size:{itemmeta['size']})"
                    )
                logger.trace(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        else:
            setattr(Slots, slotname, g.Item.id)
    except Exception as e:
        msg = (f'{g.h} Item({itemuuid}) Query KO [{e}]')
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Here everything should be OK with the equip
    try:
        # We consume the red PA (costpa) right now
        RedisPa(creatureuuid=creatureuuid).consume(redpa=costpa)
    except Exception as e:
        msg = f'{g.h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We put the info in queue for ws
    yqueue_put(
        YQ_BROADCAST,
        {
            "ciphered": False,
            "payload": Slots.as_dict(),
            "route": "mypc/{id1}/inventory/item/{id2}/equip/{id3}/{id4}",
            "scope": {
                "id": None,
                "scope": 'broadcast',
                },
            }
        )

    # We create the Creature Event
    RedisEvent().new(
        action_src=g.Creature.id,
        action_dst=None,
        action_type='action/equip',
        action_text='Equipped something',
        action_ttl=30 * 86400
        )
    # JOB IS DONE
    msg = f'{g.h} Item({itemuuid}) Equip OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "red": RedisPa(creatureuuid=creatureuuid).redpa,
                "blue": RedisPa(creatureuuid=creatureuuid).bluepa,
                "equipment": Slots.as_dict(),
            },
        }
    ), 200


# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/unequip/<string:type>/<string:slotname> # noqa
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
def inventory_item_unequip(creatureuuid, type, slotname, itemuuid):
    try:
        Slots = RedisSlots(creatureuuid=creatureuuid)
        if slotname == 'righthand':
            if Slots.righthand == itemuuid:
                if Slots.righthand == Slots.lefthand:
                    # If the weapon equipped takes both hands
                    Slots.righthand = None
                    Slots.lefthand = None
                else:
                    Slots.righthand = None
        elif slotname == 'lefthand':
            if Slots.lefthand == itemuuid:
                if Slots.righthand == Slots.lefthand:
                    # If the weapon equipped takes both hands
                    Slots.righthand = None
                    Slots.lefthand = None
                else:
                    Slots.lefthand = None
        else:
            setattr(Slots, slotname, None)
    except Exception as e:
        msg = f'{g.h} Item({itemuuid}) Unequip KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We put the info in queue for ws
    yqueue_put(
        YQ_BROADCAST,
        {
            "ciphered": False,
            "payload": Slots.as_dict(),
            "route": "mypc/{id1}/inventory/item/{id2}/unequip/{id3}/{id4}",
            "scope": {
                "id": None,
                "scope": 'broadcast',
                },
            }
        )

    # We create the Creature Event
    RedisEvent().new(
        action_src=g.Creature.id,
        action_dst=None,
        action_type='action/unequip',
        action_text='Unequipped something',
        action_ttl=30 * 86400
        )

    msg = f'{g.h} Item({itemuuid}) Unequip OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "red": RedisPa(creatureuuid=creatureuuid).redpa,
                "blue": RedisPa(creatureuuid=creatureuuid).bluepa,
                "equipment": Slots.as_dict(),
            },
        }
    ), 200


# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/offset/<int:offsetx>/<int:offsety> # noqa
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
def inventory_item_offset(creatureuuid, itemuuid, offsetx=None, offsety=None):
    try:
        g.Item.offsetx = offsetx
        g.Item.offsety = offsety
        Slots = RedisSlots(creatureuuid=g.Creature.id)
        Items = RedisSearch().item(
            query=f"@bearer:{g.Creature.id.replace('-', ' ')}"
        )
    except Exception as e:
        msg = f'{g.h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # JOB IS DONE
    msg = f'{g.h} Item({itemuuid}) Offset OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": {
                "armor": [
                    Item.as_dict() for Item in Items.results
                    if Item.metatype == 'armor'
                    ],
                "equipment": Slots.as_dict(),
                "weapon": [
                    Item.as_dict() for Item in Items.results
                    if Item.metatype == 'weapon'
                    ],
            },
        }
    ), 200
