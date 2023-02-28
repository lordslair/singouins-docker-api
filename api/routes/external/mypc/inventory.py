# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.metas                import metaNames
from nosql.queue                import yqueue_put
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet

from utils.routehelper          import (
    creature_check,
    )

from variables                  import YQ_BROADCAST


#
# Routes /mypc/<uuid:creatureuuid>/inventory/*
#
# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/dismantle
@jwt_required()
def inventory_item_dismantle(creatureuuid, itemuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if RedisPa(creatureuuid=creatureuuid).bluepa < 1:
        msg = f'{h} Not enough PA'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Item = RedisItem(itemuuid=itemuuid)
    except Exception as e:
        msg = f'{h} Item({itemuuid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Item.id is None:
            msg = f'{h} Item({itemuuid}) Query KO - NotFound'
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
        if Item.rarity == 'Broken':
            wallet_value = getattr(Wallet, Item.rarity.lower())
            setattr(Wallet, Item.rarity.lower(), wallet_value + 6)
        elif Item.rarity == 'Common':
            wallet_value = getattr(Wallet, Item.rarity.lower())
            setattr(Wallet, Item.rarity.lower(), wallet_value + 5)
        elif Item.rarity == 'Uncommon':
            wallet_value = getattr(Wallet, Item.rarity.lower())
            setattr(Wallet, Item.rarity.lower(), wallet_value + 4)
        elif Item.rarity == 'Rare':
            wallet_value = getattr(Wallet, Item.rarity.lower())
            setattr(Wallet, Item.rarity.lower(), wallet_value + 3)
        elif Item.rarity == 'Epic':
            wallet_value = getattr(Wallet, Item.rarity.lower())
            setattr(Wallet, Item.rarity.lower(), wallet_value + 2)
        elif Item.rarity == 'Legendary':
            wallet_value = getattr(Wallet, Item.rarity.lower())
            setattr(Wallet, Item.rarity.lower(), wallet_value + 1)
    except Exception as e:
        msg = f'{h} Wallet/Shards Query KO [{e}]'
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
        Item.destroy()
    except Exception as e:
        msg = f'{h} Item({itemuuid}) Query KO [{e}]'
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
        msg = f'{h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Item({itemuuid}) Dismantle OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creature": Creature.as_dict(),
                    "wallet": Wallet.as_dict(),
                    },
            }
        ), 200


# API: POST /mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/equip/<string:type>/<string:slotname> # noqa
@jwt_required()
def inventory_item_equip(creatureuuid, type, slotname, itemuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Stats = RedisStats(creatureuuid=creatureuuid)
        Item = RedisItem(itemuuid=itemuuid)
        Slots = RedisSlots(creatureuuid=creatureuuid)
    except Exception as e:
        msg = f'{h} Stats Query KO - failed [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    itemmeta = metaNames[type][Item.metaid]
    sizex, sizey = itemmeta['size'].split("x")
    costpa = round(int(sizex) * int(sizey) / 2)
    if RedisPa(creatureuuid=creatureuuid).redpa < costpa:
        msg = (
            f"{h} Not enough PA "
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
                f"{h} {carac.upper()} prequisites KO "
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
                Slots.holster = Item.id
            else:
                msg = (f"{h} Item does not fit in holster "
                       f"(itemid:{Item.id},size:{itemmeta['size']})")
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
                        Slots.righthand = Item.id
                    if equippedMeta['onehanded'] is False:
                        # A 2H weapons is in RH & LH
                        # We replace RH and clean LH
                        Slots.righthand = Item.id
                        Slots.lefthand = None
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    Slots.righthand = Item.id
                    Slots.lefthand = Item.id
            else:
                # Nothing in RH
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    Slots.righthand = Item.id
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    Slots.righthand = Item.id
                    Slots.lefthand = Item.id
        elif slotname == 'lefthand':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the left hand
                Slots.lefthand = Item.id
            else:
                msg = (
                    f"{h} Item does not fit in left hand "
                    f"(itemid:{Item.id},size:{itemmeta['size']})"
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
            setattr(Slots, slotname, Item.id)
    except Exception as e:
        msg = (f'{h} Item({itemuuid}) Query KO [{e}]')
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
        msg = f'{h} Redis Query KO [{e}]'
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
        action_src=Creature.id,
        action_dst=None,
        action_type='action/equip',
        action_text='Equipped something',
        action_ttl=30 * 86400
        )
    # JOB IS DONE
    msg = f'{h} Item({itemuuid}) Equip OK'
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
def inventory_item_unequip(creatureuuid, type, slotname, itemuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Slots = RedisSlots(creatureuuid=creatureuuid)
    except Exception as e:
        msg = f'{h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
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
        msg = f'{h} Item({itemuuid}) Unequip KO [{e}]'
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
        action_src=Creature.id,
        action_dst=None,
        action_type='action/unequip',
        action_text='Unequipped something',
        action_ttl=30 * 86400
        )

    msg = f'{h} Item({itemuuid}) Unequip OK'
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
def inventory_item_offset(creatureuuid, itemuuid, offsetx=None, offsety=None):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        Item = RedisItem(itemuuid=itemuuid)
        Item.offsetx = offsetx
        Item.offsety = offsety
    except Exception as e:
        msg = f'{h} Item({itemuuid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Slots = RedisSlots(creatureuuid=creatureuuid)
        Items = RedisSearch().item(
            query=f"@bearer:{Creature.id.replace('-', ' ')}"
        )
    except Exception as e:
        msg = f'{h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # JOB IS DONE
    msg = f'{h} Item({itemuuid}) Offset OK'
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
