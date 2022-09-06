# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_user      import fn_user_get
from mysql.methods.fn_inventory import (fn_item_get_one,
                                        fn_item_ammo_set)

from nosql.metas                import get_meta
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisWallet   import RedisWallet

# Loading the Meta for later use
try:
    metaWeapons = get_meta('weapon')
except Exception as e:
    logger.error(f'Meta fectching KO [{e}]')
else:
    logger.trace('Meta fectching OK')


#
# Routes /mypc/{pcid}/mp
#
# API: /mypc/{pcid}/action/reload/{weaponid}
@jwt_required()
def action_weapon_reload(pcid, weaponid):
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
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    # Retrieving weapon stats
    try:
        item = fn_item_get_one(weaponid)
    except Exception as e:
        msg = (f'Item Query KO '
               f'(creature.id:{creature.id},weaponid:{weaponid}) [{e}]')
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
            msg = (f'Item not found '
                   f'(creature.id:{creature.id},weaponid:{weaponid})')
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    itemmeta = dict(list(filter(lambda x: x["id"] == item.metaid,
                                metaWeapons))[0])
    if itemmeta is None:
        msg = (f'ItemMeta not found '
               f'(creature.id:{creature.id},weaponid:{item.id})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if itemmeta['pas_reload'] is None:
        msg = (f'Item is not reloadable '
               f'(creature.id:{creature.id},weaponid:{item.id})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if item.ammo == itemmeta['max_ammo']:
        msg = (f'Item is already loaded '
               f'(creature.id:{creature.id},weaponid:{item.id})')
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if RedisPa(creature).get()['red']['pa'] < itemmeta['pas_reload']:
        # Not enough PA to reload
        msg = f'Not enough PA to reload (creature.id:{creature.id})'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": {
                    "red": RedisPa(creature).get()['red'],
                    "blue": RedisPa(creature).get()['blue'],
                    "weapon": None,
                },
            }
        ), 200

    try:
        # We add the shards in the wallet
        creature_wallet = RedisWallet(creature)
        walletammo      = getattr(creature_wallet, itemmeta['caliber'])

        neededammo = itemmeta['max_ammo'] - item.ammo
        if walletammo < neededammo:
            # Not enough ammo to reload
            msg = (f"Not enough Ammo to reload "
                   f"(creature.id:{creature.id},"
                   f"cal:{itemmeta['caliber']},ammo:{walletammo}<{neededammo})"
                   )
            logger.debug(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        # We reload the weapon
        fn_item_ammo_set(weaponid, neededammo)
        # We remove the ammo from wallet
        creature_wallet.incr(itemmeta['caliber'], neededammo * (-1))
        # We consume the PA
        RedisPa(creature).set(itemmeta['pas_reload'], 0)
        # Wa add HighScore
        RedisHS(creature).incr('action_reload')
        # We create the Creature Event
        RedisEvent(creature).add(creature.id,
                                 None,
                                 'action',
                                 'Reloaded a weapon',
                                 30 * 86400)
    except Exception as e:
        msg = (f'Reload Query KO '
               f'(creature.id:{creature.id},weaponid:{item.id}) [{e}]')
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'Reload Query OK (creature.id:{creature.id},weaponid:{item.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(creature).get()['red'],
                    "blue": RedisPa(creature).get()['blue'],
                    "weapon": fn_item_get_one(weaponid),
                },
            }
        ), 200


# API: POST /mypc/{pcid}/action/unload/{weaponid}
@jwt_required()
def action_weapon_unload(pcid, weaponid):
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
    if creature.account != user.id:
        msg = (f'Token/username mismatch '
               f'(creature.id:{creature.id},username:{user})')
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 409

    # Retrieving weapon stats
    try:
        item = fn_item_get_one(weaponid)
    except Exception as e:
        msg = f'Item Query KO (pcid:{creature.id},weaponid:{weaponid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if item is None:
            msg = (f'Item not found '
                   f'(creature.id:{creature.id},weaponid:{weaponid})')
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        if item.ammo == 0:
            msg = (f'Item is already empty '
                   f'(creature.id:{creature.id},weaponid:{item.id})')
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    if RedisPa(creature).get()['blue']['pa'] < 2:
        # Not enough PA to unload
        return jsonify({"success": False,
                        "msg": f'Not enough PA to unload (pcid:{creature.id})',
                        "payload": {"red": RedisPa(creature).get()['red'],
                                    "blue": RedisPa(creature).get()['blue'],
                                    "weapon": None}}), 200

    itemmeta = dict(list(filter(lambda x: x["id"] == item.metaid,
                                metaWeapons))[0])
    if itemmeta is None:
        msg = (f'ItemMeta not found '
               f'(creature.id:{creature.id},weaponid:{item.id})')
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
        # We add the ammo to wallet
        creature_wallet.incr(itemmeta['caliber'], item.ammo)
        # We unload the weapon
        fn_item_ammo_set(weaponid, 0)
        # We consume the PA
        RedisPa(creature).set(0, 2)
        # We add HighScore
        RedisHS(creature).incr('action_unload')
        # We create the Creature Event
        RedisEvent(creature).add(creature.id,
                                 None,
                                 'action',
                                 'Unloaded a weapon',
                                 30 * 86400)
    except Exception as e:
        msg = (f'Unload Query KO '
               f'(creature.id:{creature.id},weaponid:{item.id}) [{e}]')
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'Unload Query OK (creature.id:{creature.id},weaponid:{item.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(creature).get()['red'],
                    "blue": RedisPa(creature).get()['blue'],
                    "weapon": fn_item_get_one(weaponid),
                },
            }
        ), 200
