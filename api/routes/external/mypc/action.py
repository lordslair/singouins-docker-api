# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from flask_jwt_extended         import jwt_required,get_jwt_identity

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_inventory import *

from nosql.models.RedisPa       import *
from nosql.models.RedisEvent    import *
from nosql.models.RedisHS       import *
from nosql.models.RedisWallet   import *

#
# Routes /mypc/{pcid}/mp
#
# API: /mypc/{pcid}/action/reload/{weaponid}
@jwt_required()
def action_weapon_reload(pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409

    # Retrieving weapon stats
    try:
        item = fn_item_get_one(weaponid)
    except Exception as e:
        msg = f'Item Query KO (pcid:{pc.id},weaponid:{weaponid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if item is None:
            return jsonify({"success": False,
                            "msg": f'Item not found (pcid:{pc.id},weaponid:{weaponid})',
                            "payload": None}), 200

    itemmeta = dict(list(filter(lambda x:x["id"]==item.metaid,metaWeapons))[0]) # Gruikfix
    if itemmeta is None:
        return jsonify({"success": False,
                        "msg": f'ItemMeta not found (pcid:{pcid},weaponid:{item.id})',
                        "payload": None}), 200
    if itemmeta['pas_reload'] is None:
        return jsonify({"success": False,
                        "msg": f'Item is not reloadable (pcid:{pc.id},weaponid:{item.id})',
                        "payload": None}), 200
    if item.ammo == itemmeta['max_ammo']:
        return jsonify({"success": False,
                        "msg": f'Item is already loaded (pcid:{pc.id},weaponid:{item.id})',
                        "payload": None}), 200

    if RedisPa(pc).get()['red']['pa'] < itemmeta['pas_reload']:
        # Not enough PA to reload
        return jsonify({"success": False,
                        "msg": f'Not enough PA to reload (pcid:{pc.id})',
                        "payload": {"red": RedisPa(pc).get()['red'],
                                    "blue": RedisPa(pc).get()['blue'],
                                    "action": None}}), 200

    try:
        # We add the shards in the wallet
        redis_wallet = RedisWallet(pc)

        if   itemmeta['caliber'] == '.22':   walletammo = redis_wallet.cal22
        elif itemmeta['caliber'] == '.223':  walletammo = redis_wallet.cal223
        elif itemmeta['caliber'] == '.311':  walletammo = redis_wallet.cal311
        elif itemmeta['caliber'] == '.50':   walletammo = redis_wallet.cal50
        elif itemmeta['caliber'] == '.55':   walletammo = redis_wallet.cal55
        elif itemmeta['caliber'] == 'shell': walletammo = redis_wallet.shell
        elif itemmeta['caliber'] == 'bolt':  walletammo = redis_wallet.bolt
        elif itemmeta['caliber'] == 'arrow': walletammo = redis_wallet.arrow

        neededammo = itemmeta['max_ammo'] - item.ammo
        if walletammo < neededammo:
            # Not enough ammo to reload
            msg = (f"Not enough Ammo to reload (pcid:{pc.id},"
                   f"cal:{itemmeta['caliber']},ammo:{walletammo}<{neededammo})")
            logger.debug(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200

        # We reload the weapon
        fn_item_ammo_set(weaponid,neededammo)
        # We remove the ammo from wallet
        if   itemmeta['caliber'] == '.22':   redis_wallet.cal22  -= neededammo
        elif itemmeta['caliber'] == '.223':  redis_wallet.cal223 -= neededammo
        elif itemmeta['caliber'] == '.311':  redis_wallet.cal311 -= neededammo
        elif itemmeta['caliber'] == '.50':   redis_wallet.cal50  -= neededammo
        elif itemmeta['caliber'] == '.55':   redis_wallet.cal55  -= neededammo
        elif itemmeta['caliber'] == 'shell': redis_wallet.shell  -= neededammo
        elif itemmeta['caliber'] == 'bolt':  redis_wallet.bolt   -= neededammo
        elif itemmeta['caliber'] == 'arrow': redis_wallet.arrow  -= neededammo
        # We store the Wallet
        redis_wallet.store()
        # We consume the PA
        RedisPa(pc).set(itemmeta['pas_reload'],0)
        # Wa add HighScore
        RedisHS(pc).incr('action_reload')
        # We create the Creature Event
        RedisEvent(pc).add(pc.id,
                           None,
                           'action',
                           f'Reloaded a weapon',
                           30*86400)
    except Exception as e:
        msg = f'Weapon reload KO (pcid:{pc.id},weaponid:{item.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Weapon reload OK (pcid:{pc.id},weaponid:{item.id})',
                        "payload": {"red": RedisPa(pc).get()['red'],
                                    "blue": RedisPa(pc).get()['blue'],
                                    "weapon": fn_item_get_one(weaponid)}}), 200

# API: POST /mypc/{pcid}/action/unload/{weaponid}
@jwt_required()
def action_weapon_unload(pcid,weaponid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if pc is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (pcid:{pcid})',
                        "payload": None}), 200
    if pc.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (pcid:{pc.id},username:{user.name})',
                        "payload": None}), 409

    # Retrieving weapon stats
    try:
        item = fn_item_get_one(weaponid)
    except Exception as e:
        msg = f'Item Query KO (pcid:{pc.id},weaponid:{weaponid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if item is None:
            return jsonify({"success": False,
                            "msg": f'Item not found (pcid:{pc.id},weaponid:{weaponid})',
                            "payload": None}), 200
        if item.ammo == 0:
            return jsonify({"success": False,
                            "msg": f'Item is already empty (pcid:{pc.id},weaponid:{weaponid})',
                            "payload": None}), 200

    if RedisPa(pc).get()['blue']['pa'] < 2:
        # Not enough PA to unload
        return jsonify({"success": False,
                        "msg": f'Not enough PA to unload (pcid:{pc.id})',
                        "payload": {"red": RedisPa(pc).get()['red'],
                                    "blue": RedisPa(pc).get()['blue'],
                                    "action": None}}), 200

    itemmeta = dict(list(filter(lambda x:x["id"]==item.metaid,metaWeapons))[0]) # Gruikfix
    if itemmeta is None:
        return jsonify({"success": False,
                        "msg": f'ItemMeta not found (pcid:{pcid},weaponid:{item.id})',
                        "payload": None}), 200

    try:
        # We add the shards in the wallet
        redis_wallet = RedisWallet(pc)
        # We add the ammo to wallet
        if   itemmeta['caliber'] == '.22':   redis_wallet.cal22  += item.ammo
        elif itemmeta['caliber'] == '.223':  redis_wallet.cal223 += item.ammo
        elif itemmeta['caliber'] == '.311':  redis_wallet.cal311 += item.ammo
        elif itemmeta['caliber'] == '.50':   redis_wallet.cal50  += item.ammo
        elif itemmeta['caliber'] == '.55':   redis_wallet.cal55  += item.ammo
        elif itemmeta['caliber'] == 'shell': redis_wallet.shell  += item.ammo
        elif itemmeta['caliber'] == 'bolt':  redis_wallet.bolt   += item.ammo
        elif itemmeta['caliber'] == 'arrow': redis_wallet.arrow  += item.ammo
        # We store the Wallet
        redis_wallet.store()
        # We unload the weapon
        fn_item_ammo_set(weaponid,0)
        # We consume the PA
        RedisPa(pc).set(0,2)
        # We add HighScore
        RedisHS(pc).incr('action_unload')
        # We create the Creature Event
        RedisEvent(pc).add(pc.id,
                           None,
                           'action',
                           f'Unloaded a weapon',
                           30*86400)
    except Exception as e:
        msg = f'Weapon unload KO (pcid:{pc.id},weaponid:{weaponid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f'Weapon unload OK (pcid:{pc.id},weaponid:{item.id})',
                        "payload": {"red": RedisPa(pc).get()['red'],
                                    "blue": RedisPa(pc).get()['blue'],
                                    "weapon": fn_item_get_one(weaponid)}}), 200
