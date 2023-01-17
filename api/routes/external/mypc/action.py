# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.metas                import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisWallet   import RedisWallet

from utils.routehelper          import (
    creature_check,
    )

#
# Routes /mypc/{pcid}/action
#


# API: /mypc/{pcid}/action/reload/{weaponid}
@jwt_required()
def action_weapon_reload(pcid, weaponid):
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, get_jwt_identity())

    # Retrieving weapon stats
    try:
        item = RedisItem(Creature).get(weaponid)
    except Exception as e:
        msg = f'{h} Item Query KO (weaponid:{weaponid}) [{e}]'
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
            msg = f'{h} Item not found (weaponid:{weaponid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    itemmeta = metaNames[item.metatype][item.metaid]
    if itemmeta is None:
        msg = f'{h} metaNames Query KO - NotFound (weaponid:{weaponid})'
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

    if itemmeta['pas_reload'] is None:
        msg = f'{h} Item is not reloadable (weaponid:{item.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if item.ammo == itemmeta['max_ammo']:
        msg = f'{h} Item is already loaded (weaponid:{item.id})'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    creature_pa = RedisPa(Creature)
    if creature_pa.redpa < itemmeta['pas_reload']:
        # Not enough PA to reload
        msg = f'{h} Not enough PA to reload'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": {
                    "red": creature_pa._asdict()['red'],
                    "blue": creature_pa._asdict()['blue'],
                    "weapon": None,
                },
            }
        ), 200

    try:
        # We add the shards in the wallet
        creature_wallet = RedisWallet(Creature)
        walletammo      = getattr(creature_wallet, itemmeta['caliber'])

        neededammo = itemmeta['max_ammo'] - item.ammo
        if walletammo < neededammo:
            # Not enough ammo to reload
            msg = (f"{h} Not enough Ammo to reload "
                   f"(cal:{itemmeta['caliber']},"
                   f"ammo:{walletammo}<{neededammo})"
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
        item.ammo = neededammo
        # We remove the ammo from wallet
        setattr(creature_wallet, itemmeta['caliber'], walletammo - neededammo)
        # We consume the PA
        RedisPa(Creature).consume(redpa=itemmeta['pas_reload'])
        # Wa add HighScore
        RedisHS(Creature).incr('action_reload')
        # We create the Creature Event
        RedisEvent().new(
            action_src=Creature.id,
            action_dst=None,
            action_type='action/reload',
            action_text='Reloaded a weapon',
            action_ttl=30 * 86400
            )
    except Exception as e:
        msg = f'{h} Reload Query KO (weaponid:{item.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Reload Query OK (weaponid:{item.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(Creature)._asdict()['red'],
                    "blue": RedisPa(Creature)._asdict()['blue'],
                    "weapon": RedisItem(Creature).get(weaponid)._asdict(),
                },
            }
        ), 200


# API: POST /mypc/{pcid}/action/unload/{weaponid}
@jwt_required()
def action_weapon_unload(pcid, weaponid):
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, get_jwt_identity())

    # Retrieving weapon stats
    try:
        item = RedisItem(Creature).get(weaponid)
    except Exception as e:
        msg = f'{h} Item Query KO (weaponid:{weaponid}) [{e}]'
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
            msg = f'{h} Item not found (weaponid:{weaponid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        if item.ammo == 0:
            msg = f'{h} Item is already empty (weaponid:{item.id})'
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    creature_pa = RedisPa(Creature)
    if creature_pa.bluepa < 2:
        # Not enough PA to unload
        msg = f'{h} Not enough PA to unload (weaponid:{item.id})'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": {
                    "red": RedisPa(Creature)._asdict()['red'],
                    "blue": RedisPa(Creature)._asdict()['blue'],
                    "weapon": None,
                },
            }
        ), 200

    itemmeta = metaNames[item.metatype][item.metaid]
    if itemmeta is None:
        msg = f'{h} metaNames Query KO - NotFound (weaponid:{weaponid})'
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

    try:
        # We add the shards in the wallet
        creature_wallet = RedisWallet(Creature)
        # We add the ammo to wallet
        walletammo = getattr(creature_wallet, itemmeta['caliber'])
        setattr(creature_wallet, itemmeta['caliber'], walletammo + item.ammo)
        # We unload the weapon
        item.ammo = 0
        # We consume the PA
        RedisPa(Creature).consume(bluepa=2)
        # We add HighScore
        RedisHS(Creature).incr('action_unload')
        # We create the Creature Event
        RedisEvent().new(
            action_src=Creature.id,
            action_dst=None,
            action_type='action/unload',
            action_text='Unloaded a weapon',
            action_ttl=30 * 86400
            )
    except Exception as e:
        msg = f'{h} Unload Query KO (weaponid:{item.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Unload Query OK (weaponid:{item.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": RedisPa(Creature)._asdict()['red'],
                    "blue": RedisPa(Creature)._asdict()['blue'],
                    "weapon": RedisItem(Creature).get(weaponid)._asdict(),
                },
            }
        ), 200
