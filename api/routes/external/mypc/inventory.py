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
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet

from utils.routehelper          import (
    creature_check,
    )

from variables                  import YQ_BROADCAST

#
# Routes /mypc/{pcid}/inventory/*
#


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle
@jwt_required()
def inventory_item_dismantle(pcid, itemid):
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, get_jwt_identity())

    if RedisPa(Creature).bluepa < 1:
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
        item = RedisItem(Creature).get(itemid)
    except Exception as e:
        msg = f'{h} Item Query KO - failed (itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if item is None:
            msg = f'{h} Item Query KO - Not found (itemid:{itemid})'
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
        creature_wallet = RedisWallet(Creature)
        if item.rarity == 'Broken':
            wallet_value = getattr(creature_wallet, item.rarity.lower())
            setattr(creature_wallet, item.rarity.lower(), wallet_value + 6)
        elif item.rarity == 'Common':
            wallet_value = getattr(creature_wallet, item.rarity.lower())
            setattr(creature_wallet, item.rarity.lower(), wallet_value + 5)
        elif item.rarity == 'Uncommon':
            wallet_value = getattr(creature_wallet, item.rarity.lower())
            setattr(creature_wallet, item.rarity.lower(), wallet_value + 4)
        elif item.rarity == 'Rare':
            wallet_value = getattr(creature_wallet, item.rarity.lower())
            setattr(creature_wallet, item.rarity.lower(), wallet_value + 3)
        elif item.rarity == 'Epic':
            wallet_value = getattr(creature_wallet, item.rarity.lower())
            setattr(creature_wallet, item.rarity.lower(), wallet_value + 2)
        elif item.rarity == 'Legendary':
            wallet_value = getattr(creature_wallet, item.rarity.lower())
            setattr(creature_wallet, item.rarity.lower(), wallet_value + 1)
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
        RedisItem(Creature).destroy(itemid)
    except Exception as e:
        msg = f'{h} Item Query KO (pcid:{Creature.id}) [{e}]'
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
        RedisPa(Creature).consume(bluepa=1)
        # We add HighScore
        RedisHS(Creature).incr('action_dismantle')
    except Exception as e:
        msg = f'{h} Redis Query KO (pcid:{Creature.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # JOB IS DONE
        msg = f'{h} Item dismantle OK (pcid:{Creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creature": Creature._asdict(),
                    "wallet": creature_wallet._asdict(),
                },
            }
        ), 200


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname> # noqa
@jwt_required()
def inventory_item_equip(pcid, type, slotname, itemid):
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        creature_stats = RedisStats(Creature)._asdict()
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
    else:
        if creature_stats is None:
            msg = f'{h} Stats Query KO - Not found'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    try:
        item = RedisItem(Creature).get(itemid)
    except Exception as e:
        msg = f'{h} Item Query KO - failed (itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if item is None:
            msg = f'{h} Item Query KO - Not found (itemid:{itemid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    itemmeta = metaNames[type][item.metaid]
    if itemmeta is None:
        msg = f'{h} metaNames Query KO - NotFound (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 404
    else:
        logger.trace(f'{h} metaNames: {itemmeta}')

    sizex, sizey = itemmeta['size'].split("x")
    costpa       = round(int(sizex) * int(sizey) / 2)
    if RedisPa(Creature).redpa < costpa:
        msg = (f"{h} Not enough PA "
               f"(redpa:{RedisPa(Creature).redpa},cost:{costpa})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-requisite checks
    if itemmeta['min_m'] > creature_stats['base']['m']:
        msg = (f"{h} M prequisites failed "
               f"(m_min:{itemmeta['min_m']},m:{creature_stats['base']['m']})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    elif itemmeta['min_r'] > creature_stats['base']['r']:
        msg = (f"{h} R prequisites failed "
               f"(r_min:{itemmeta['min_r']},r:{creature_stats['base']['r']})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    elif itemmeta['min_g'] > creature_stats['base']['g']:
        msg = (f"{h} G prequisites failed "
               f"(g_min:{itemmeta['min_g']},g:{creature_stats['base']['g']})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    elif itemmeta['min_v'] > creature_stats['base']['v']:
        msg = (f"{h} V prequisites failed "
               f"(v_min:{itemmeta['min_v']},v:{creature_stats['base']['v']})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    elif itemmeta['min_p'] > creature_stats['base']['p']:
        msg = (f"{h} P prequisites failed "
               f"(p_min:{itemmeta['min_p']},p:{creature_stats['base']['p']})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    elif itemmeta['min_b'] > creature_stats['base']['b']:
        msg = (f"{h} B prequisites failed "
               f"(b_min:{itemmeta['min_b']},b:{creature_stats['base']['b']})")
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        creature_slots = RedisSlots(Creature)
    except Exception as e:
        msg = f'{h} Slots Query KO - failed [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_slots is None:
            msg = f'{h} Slots Query KO - Not found (itemid:{itemid})'
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
                creature_slots.holster = item.id
            else:
                msg = (f"{h} Item does not fit in holster "
                       f"(itemid:{item.id},size:{itemmeta['size']})")
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        elif slotname == 'righthand':
            if creature_slots.righthand:
                # Something is already equipped in RH
                equipped = RedisItem(Creature).get(creature_slots.righthand)
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    equippedMeta = metaNames['weapon'][equipped.metaid]
                    if equippedMeta['onehanded'] is True:
                        # A 1H weapons is in RH : we replace
                        creature_slots.righthand = item.id
                    if equippedMeta['onehanded'] is False:
                        # A 2H weapons is in RH & LH
                        # We replace RH and clean LH
                        creature_slots.righthand = item.id
                        creature_slots.lefthand = None
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    creature_slots.righthand = item.id
                    creature_slots.lefthand = item.id
            else:
                # Nothing in RH
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    creature_slots.righthand = item.id
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    creature_slots.righthand = item.id
                    creature_slots.lefthand = item.id
        elif slotname == 'lefthand':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the left hand
                creature_slots.lefthand = item.id
            else:
                msg = (f"{h} Item does not fit in left hand "
                       f"(itemid:{item.id},size:{itemmeta['size']})")
                logger.trace(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        else:
            setattr(creature_slots, slotname, item.id)
    except Exception as e:
        msg = (f'{h} Slots Query KO - failed (itemid:{itemid}) [{e}]')
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
        RedisPa(Creature).consume(redpa=costpa)
    except Exception as e:
        msg = f'{h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We put the info in queue for ws
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": creature_slots._asdict(),
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
        msg = f'{h} Equip Query OK (itemid:{itemid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(Creature)._asdict()['red'],
                    "blue": RedisPa(Creature)._asdict()['blue'],
                    "equipment": creature_slots._asdict(),
                },
            }
        ), 200


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname> # noqa
@jwt_required()
def inventory_item_unequip(pcid, type, slotname, itemid):
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        creature_slots = RedisSlots(Creature)
    except Exception as e:
        msg = f'{h} Slots Query KO - failed [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if creature_slots is None:
            msg = f'{h} Slots Query KO - Not found (itemid:{itemid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    try:
        if slotname == 'righthand':
            if creature_slots.righthand == itemid:
                if creature_slots.righthand == creature_slots.lefthand:
                    # If the weapon equipped takes both hands
                    creature_slots.righthand = None
                    creature_slots.lefthand = None
                else:
                    creature_slots.righthand = None
        elif slotname == 'lefthand':
            if creature_slots.lefthand == itemid:
                if creature_slots.righthand == creature_slots.lefthand:
                    # If the weapon equipped takes both hands
                    creature_slots.righthand = None
                    creature_slots.lefthand = None
                else:
                    creature_slots.lefthand = None
        else:
            setattr(creature_slots, slotname, None)
    except Exception as e:
        msg = f'{h} Slots Query KO - failed (itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    # Here everything should be OK with the unequip
    else:
        # We put the info in queue for ws
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": creature_slots._asdict(),
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
        # JOB IS DONE
        msg = f'{h} Unequip Query OK (itemid:{itemid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(Creature)._asdict()['red'],
                    "blue": RedisPa(Creature)._asdict()['blue'],
                    "equipment": creature_slots._asdict(),
                },
            }
        ), 200


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety> # noqa
@jwt_required()
def inventory_item_offset(pcid, itemid, offsetx=None, offsety=None):
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, get_jwt_identity())

    try:
        item = RedisItem(Creature).get(itemid)
    except Exception as e:
        msg = f'{h} Item Query KO - failed (itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if item is None:
            msg = f'{h} Item Query KO - Not found (itemid:{itemid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    try:
        item.offsetx = offsetx
        item.offsety = offsety
    except Exception as e:
        msg = f'{h} Item Query KO - failed (itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        bearer = Creature.id.replace('-', ' ')
        creature_inventory = RedisItem(Creature).search(
            field='bearer', query=f'{bearer}'
            )

        armor = [x for x in creature_inventory if x['metatype'] == 'armor']
        weapon = [x for x in creature_inventory if x['metatype'] == 'weapon']

        creature_slots = RedisSlots(Creature)

        # JOB IS DONE
        msg = f'{h} Offset Query OK (itemid:{itemid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "armor": armor,
                    "equipment": creature_slots._asdict(),
                    "weapon": weapon,
                },
            }
        ), 200
