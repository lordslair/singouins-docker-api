# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_inventory import *
from mysql.methods.fn_wallet    import fn_wallet_shards_add

from nosql.models.RedisPa       import *
from nosql.models.RedisStats    import *
from nosql                      import *

#
# Routes /mypc/{pcid}/pa
#
# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle
@jwt_required()
def inventory_item_dismantle(pcid,itemid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409
    if RedisPa(pc).get()['blue']['pa'] < 1:
        return jsonify({"success": False,
                        "msg": f'Not enough PA (pcid:{pcid})',
                        "payload": None}), 200

    try:
        item = fn_item_get_one(itemid)
    except Exception as e:
        msg = f'Item Query KO - failed (pcid:{pc.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if item is None:
            msg = f'Item Query KO - Not found (pcid:{pc.id},itemid:{itemid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    if   item.rarity == 'Broken':
        shards = [6,0,0,0,0,0]
        incr.many(f'highscores:{pc.id}:action:dismantle:shards:{item.rarity}', shards[0])
    elif item.rarity == 'Common':
        shards = [0,5,0,0,0,0]
        incr.many(f'highscores:{pc.id}:action:dismantle:shards:{item.rarity}', shards[1])
    elif item.rarity == 'Uncommon':
        shards = [0,0,4,0,0,0]
        incr.many(f'highscores:{pc.id}:action:dismantle:shards:{item.rarity}', shards[2])
    elif item.rarity == 'Rare':
        shards = [0,0,0,3,0,0]
        incr.many(f'highscores:{pc.id}:action:dismantle:shards:{item.rarity}', shards[3])
    elif item.rarity == 'Epic':
        shards = [0,0,0,0,2,0]
        incr.many(f'highscores:{pc.id}:action:dismantle:shards:{item.rarity}', shards[4])
    elif item.rarity == 'Legendary':
        shards = [0,0,0,0,0,1]
        incr.many(f'highscores:{pc.id}:action:dismantle:shards:{item.rarity}', shards[5])

    try:
        # We add the shards in the wallet
        wallet = fn_wallet_shards_add(pc,shards)
    except Exception as e:
        msg = f'Wallet/Shards Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        # We destroy the item
        fn_item_del(pc,item.id)
    except Exception as e:
        msg = f'Item Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        # We consume the blue PA (1)
        RedisPa(pc).set(0,1)
        # We add HighScore
        incr.many(f'highscores:{pc.id}:action:dismantle:items', 1)
    except Exception as e:
        msg = f'Redis Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # JOB IS DONE
        return jsonify({"success": True,
                        "msg": f'Item dismantle OK (pcid:{pc.id})',
                        "payload": {"shards": {"Broken":    shards[0],
                                               "Common":    shards[1],
                                               "Uncommon":  shards[2],
                                               "Rare":      shards[3],
                                               "Epic":      shards[4],
                                               "Legendary": shards[5]},
                                    "wallet": wallet}}), 200

# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname>
@jwt_required()
def inventory_item_equip(pcid,type,slotname,itemid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409

    # Loading the Meta for later use
    try:
        metaWeapons = metas.get_meta('weapon')
        metaArmors  = metas.get_meta('armor')
    except Exception as e:
        msg = f'Meta fectching: KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        logger.trace(f'Meta fectching: OK')

    try:
        creature_stats = RedisStats(pc).refresh().dict
    except Exception as e:
        msg = f'Stats Query KO - failed (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if creature_stats is None:
            msg = f'Stats Query KO - Not found (pcid:{pc.id})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        item = fn_item_get_one(itemid)
    except Exception as e:
        msg = f'Item Query KO - failed (pcid:{pc.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if item is None:
            msg = f'Item Query KO - Not found (pcid:{pc.id},itemid:{itemid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    if   type == 'weapon':
         itemmeta = dict(list(filter(lambda x:x["id"]==item.metaid,metaWeapons))[0]) # GruikFix
    elif type == 'armor':
         itemmeta = dict(list(filter(lambda x:x["id"]==item.metaid,metaArmors))[0]) # Gruikfix
    if itemmeta is None:
        msg = f'ItemMeta Query KO - Not found (pcid:{pc.id},itemid:{itemid})'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    sizex,sizey = itemmeta['size'].split("x")
    costpa      = round(int(sizex) * int(sizey) / 2)
    if RedisPa(pc).get()['red']['pa'] < costpa:
        msg = f"Not enough PA (pcid:{pc.id},redpa:{RedisPa(pc).get()['red']['pa']},cost:{costpa})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Pre-requisite checks
    if itemmeta['min_m'] > creature_stats['base']['m']:
        msg = f"M prequisites failed (m_min:{itemmeta['min_m']},m:{creature_stats['base']['m']})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    elif itemmeta['min_r'] > creature_stats['base']['r']:
        msg = f"R prequisites failed (r_min:{itemmeta['min_r']},r:{creature_stats['base']['r']})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    elif itemmeta['min_g'] > creature_stats['base']['g']:
        msg = f"G prequisites failed (g_min:{itemmeta['min_g']},g:{creature_stats['base']['g']})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    elif itemmeta['min_v'] > creature_stats['base']['v']:
        msg = f"V prequisites failed (v_min:{itemmeta['min_v']},v:{creature_stats['base']['v']})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    elif itemmeta['min_p'] > creature_stats['base']['p']:
        msg = f"P prequisites failed (p_min:{itemmeta['min_p']},p:{creature_stats['base']['p']})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    elif itemmeta['min_b'] > creature_stats['base']['b']:
        msg = f"B prequisites failed (b_min:{itemmeta['min_b']},b:{creature_stats['base']['b']})"
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    try:
        equipment = fn_slots_get_one(pc)
    except Exception as e:
        msg = f'Slots Query KO - failed (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if equipment is None:
            msg = f'Slots Query KO - Not found (pcid:{pc.id},itemid:{itemid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        # The item to equip exists, is owned by the PC, and we retrieved his equipment from DB
        if slotname == 'holster':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the holster
                fn_slots_set_one(pc,slotname,item.id)
            else:
                return jsonify({"success": False,
                                "msg": f"Item does not fit in holster (itemid:{item.id},size:{itemmeta['size']})",
                                "payload": None}), 200
        elif slotname == 'righthand':
            if equipment.righthand:
                # Something is already equipped in RH
                equipped = fn_item_get_one(equipment.righthand)
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    if metaWeapons[equipped.metaid-1]['onehanded'] is True:
                        # A 1H weapons is in RH : we replace
                        fn_slots_set_one(pc,'righthand',item.id)
                    if metaWeapons[equipped.metaid-1]['onehanded'] is False:
                        # A 2H weapons is in RH & LH : we replace RH and clean LH
                        fn_slots_set_one(pc,'righthand',item.id)
                        fn_slots_set_one(pc,'lefthand',None)
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    fn_slots_set_one(pc,'righthand',item.id)
                    fn_slots_set_one(pc,'lefthand',item.id)
            else:
                # Nothing in RH
                # We equip a 1H weapon
                if int(sizex) * int(sizey) <= 6:
                    fn_slots_set_one(pc,'righthand',item.id)
                # We equip a 2H weapon
                if int(sizex) * int(sizey) > 6:
                    # It is a 2H weapon: it fits inside the RH & LH
                    fn_slots_set_one(pc,'righthand',item.id)
                    fn_slots_set_one(pc,'lefthand',item.id)
        elif slotname == 'lefthand':
            if int(sizex) * int(sizey) <= 4:
                # It fits inside the left hand
                fn_slots_set_one(pc,slotname,item.id)
            else:
                return jsonify({"success": False,
                                "msg": f"Item does not fit in left hand (itemid:{item.id},size:{itemmeta['size']})",
                                "payload": None}), 200
        else:
            fn_slots_set_one(pc,slotname,item.id)
    except Exception as e:
        msg = f'Slots Query KO - failed (pcid:{pc.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Here everything should be OK with the equip
    try:
        # We consume the red PA (costpa) right now
        RedisPa(pc).set(costpa,0)
    except Exception as e:
        msg = f'Redis Query KO (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        equipment = fn_slots_get_one(pc)

        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": equipment,
                "route": "mypc/{id1}/inventory/item/{id2}/equip/{id3}/{id4}",
                "scope": {"id": None, "scope": 'broadcast'}}
        queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

        # We create the Creature Event
        events.set_event(pc.id,
                         None,
                         'item',
                         'Equipped something',
                         30*86400)
        # JOB IS DONE
        msg = f'Equip Query OK (pcid:{pc.id},itemid:{itemid})'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": {"red": RedisPa(pc).get()['red'],
                                    "blue": RedisPa(pc).get()['blue'],
                                    "equipment": equipment}}), 200

# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname>
@jwt_required()
def inventory_item_unequip(pcid,type,slotname,itemid):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409

    try:
        equipment = fn_slots_get_one(pc)
    except Exception as e:
        msg = f'Slots Query KO - failed (pcid:{pc.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if equipment is None:
            msg = f'Slots Query KO - Not found (pcid:{pc.id},itemid:{itemid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

    try:
        if slotname == 'righthand':
            if equipment.righthand == itemid:
                if equipment.righthand ==  equipment.lefthand:
                    # If the weapon equipped takes both hands
                    fn_slots_set_one(pc,'righthand',None)
                    fn_slots_set_one(pc,'lefthand',None)
                else:
                    fn_slots_set_one(pc,slotname,None)
        elif slotname == 'lefthand':
            if equipment.lefthand == itemid:
                if equipment.righthand ==  equipment.lefthand:
                    # If the weapon equipped takes both hands
                    fn_slots_set_one(pc,'righthand',None)
                    fn_slots_set_one(pc,'lefthand',None)
                else:
                    fn_slots_set_one(pc,slotname,None)
        else:
            fn_slots_set_one(pc,slotname,None)
    except Exception as e:
        msg = f'Slots Query KO - failed (pcid:{pc.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    # Here everything should be OK with the unequip
    else:
        equipment = fn_slots_get_one(pc)

        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": equipment,
                "route": "mypc/{id1}/inventory/item/{id2}/unequip/{id3}/{id4}",
                "scope": {"id": None, "scope": 'broadcast'}}
        queue.yqueue_put('broadcast', json.loads(jsonify(qmsg).get_data()))

        # JOB IS DONE
        msg = f'Unequip Query OK (pcid:{pc.id},itemid:{itemid})'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": {"red": RedisPa(pc).get()['red'],
                                    "blue": RedisPa(pc).get()['blue'],
                                    "equipment": equipment}}), 200

# API: POST /mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety>
@jwt_required()
def inventory_item_offset(pcid,itemid,offsetx = None,offsety = None):
    pc       = fn_creature_get(None,pcid)[3]
    user     = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{username})',
                        "payload": None}), 409

    try:
        item = fn_item_get_one(itemid)
    except Exception as e:
        msg = f'Item Query KO - failed (pcid:{pc.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if item is None:
            msg = f'Item Query KO - Not found (pcid:{pc.id},itemid:{itemid})'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200


    try:
        item = fn_item_offset_set(itemid,offsetx,offsety)
    except Exception as e:
        msg = f'Item Query KO - failed (pcid:{pc.id},itemid:{itemid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        all_items_sql  = fn_item_get_all(pc)
        all_items_json = json.loads(jsonify(all_items_sql).get_data())

        armor     = [x for x in all_items_json if x['metatype'] == 'armor']
        weapon    = [x for x in all_items_json if x['metatype'] == 'weapon']
        equipment = fn_slots_get_all(pc)

        # JOB IS DONE
        msg = f'Offset Query OK (pcid:{pc.id},itemid:{itemid})'
        logger.trace(msg)
        return jsonify({"success": True,
                        "msg": msg,
                        "payload": {"armor":     armor,
                                    "equipment": equipment,
                                    "weapon":    weapon}}), 200
