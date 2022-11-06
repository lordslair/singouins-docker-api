# -*- coding: utf8 -*-

import json

from flask                               import jsonify
from flask_jwt_extended                  import (jwt_required,
                                                 get_jwt_identity)
from loguru                              import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get

from nosql.metas                import metaArmors, metaWeapons
from nosql.queue                import yqueue_put
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet


#
# Routes /mypc/{pcid}/inventory/*
#
# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle
@jwt_required()
def inventory_item_dismantle(pcid, itemid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409
    if RedisPa(creature).bluepa < 1:
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
        item = RedisItem(creature).get(itemid)
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
        creature_wallet = RedisWallet(creature)
        if item.rarity == 'Broken':
            creature_wallet.incr(item.rarity.lower(), 6)
        elif item.rarity == 'Common':
            creature_wallet.incr(item.rarity.lower(), 5)
        elif item.rarity == 'Uncommon':
            creature_wallet.incr(item.rarity.lower(), 4)
        elif item.rarity == 'Rare':
            creature_wallet.incr(item.rarity.lower(), 3)
        elif item.rarity == 'Epic':
            creature_wallet.incr(item.rarity.lower(), 2)
        elif item.rarity == 'Legendary':
            creature_wallet.incr(item.rarity.lower(), 1)
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
        RedisItem(creature).destroy(itemid)
    except Exception as e:
        msg = f'{h} Item Query KO (pcid:{creature.id}) [{e}]'
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
        RedisPa(creature).consume(bluepa=1)
        # We add HighScore
        RedisHS(creature).incr('action_dismantle')
    except Exception as e:
        msg = f'{h} Redis Query KO (pcid:{creature.id}) [{e}]'
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
        msg = f'{h} Item dismantle OK (pcid:{creature.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creature": creature,
                    "wallet": creature_wallet._asdict(),
                },
            }
        ), 200


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname> # noqa
@jwt_required()
def inventory_item_equip(pcid, type, slotname, itemid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        creature_stats = RedisStats(creature)._asdict()
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
        item = RedisItem(creature).get(itemid)
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

    if type == 'weapon':
        itemmeta = dict(list(filter(lambda x: x["id"] == item.metaid,
                                    metaWeapons))[0])  # GruikFix
    elif type == 'armor':
        itemmeta = dict(list(filter(lambda x: x["id"] == item.metaid,
                                    metaArmors))[0])  # Gruikfix
    if itemmeta is None:
        msg = f'{h} ItemMeta Query KO - Not found (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    sizex, sizey = itemmeta['size'].split("x")
    costpa       = round(int(sizex) * int(sizey) / 2)
    if RedisPa(creature).redpa < costpa:
        msg = (f"{h} Not enough PA "
               f"(redpa:{RedisPa(creature).redpa},cost:{costpa})")
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
        creature_slots = RedisSlots(creature)
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
                equipped = RedisItem(creature).get(creature_slots.righthand)
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    if metaWeapons[equipped.metaid - 1]['onehanded'] is True:
                        # A 1H weapons is in RH : we replace
                        creature_slots.righthand = item.id
                    if metaWeapons[equipped.metaid - 1]['onehanded'] is False:
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
        RedisPa(creature).consume(redpa=costpa)
    except Exception as e:
        msg = f'{h} Redis Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": creature_slots._asdict(),
                "route": "mypc/{id1}/inventory/item/{id2}/equip/{id3}/{id4}",
                "scope": {"id": None, "scope": 'broadcast'}}
        yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

        # We create the Creature Event
        RedisEvent(creature).add(creature.id,
                                 None,
                                 'item',
                                 'Equipped something',
                                 30 * 86400)
        # JOB IS DONE
        msg = f'{h} Equip Query OK (itemid:{itemid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(creature)._asdict()['red'],
                    "blue": RedisPa(creature)._asdict()['blue'],
                    "equipment": creature_slots._asdict(),
                },
            }
        ), 200


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname> # noqa
@jwt_required()
def inventory_item_unequip(pcid, type, slotname, itemid):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        creature_slots = RedisSlots(creature)
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
        qmsg = {"ciphered": False,
                "payload": creature_slots._asdict(),
                "route": "mypc/{id1}/inventory/item/{id2}/unequip/{id3}/{id4}",
                "scope": {"id": None, "scope": 'broadcast'}}
        yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

        # JOB IS DONE
        msg = f'{h} Unequip Query OK (itemid:{itemid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(creature)._asdict()['red'],
                    "blue": RedisPa(creature)._asdict()['blue'],
                    "equipment": creature_slots._asdict(),
                },
            }
        ), 200


# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety> # noqa
@jwt_required()
def inventory_item_offset(pcid, itemid, offsetx=None, offsety=None):
    creature = fn_creature_get(None, pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature not found (creatureid:{pcid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{creature.id}]'  # Header for logging
    if creature.account != user.id:
        msg = (f'{h} Token/username mismatch '
               f'(username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    try:
        item = RedisItem(creature).get(itemid)
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
        creature_inventory = RedisItem(creature).search(
            field='bearer', query=f'[{creature.id} {creature.id}]'
            )

        armor = [x for x in creature_inventory if x['metatype'] == 'armor']
        weapon = [x for x in creature_inventory if x['metatype'] == 'weapon']

        creature_slots = RedisSlots(creature)

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
