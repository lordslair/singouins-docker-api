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
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: /mypc/<uuid:creatureuuid>/action/reload/<uuid:weaponuuid>
@jwt_required()
def reload(creatureuuid, weaponuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    # Retrieving weapon stats
    try:
        Item = RedisItem(itemuuid=weaponuuid)
    except Exception as e:
        msg = f'{h} Item Query KO (weaponuuid:{weaponuuid}) [{e}]'
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
            msg = f'{h} Item not found (weaponid:{weaponuuid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    itemmeta = metaNames[Item.metatype][Item.metaid]
    if itemmeta is None:
        msg = f'{h} metaNames Query KO - NotFound (weaponid:{weaponuuid})'
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
        msg = f'{h} Item is not reloadable (weaponid:{Item.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Item.ammo == itemmeta['max_ammo']:
        msg = f'{h} Item is already loaded (weaponid:{Item.id})'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    Pa = RedisPa(creatureuuid=creatureuuid)
    if Pa.redpa < itemmeta['pas_reload']:
        # Not enough PA to reload
        msg = f'{h} Not enough PA to reload'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": {
                    "red": Pa.as_dict()['red'],
                    "blue": Pa.as_dict()['blue'],
                    "weapon": None,
                },
            }
        ), 200

    try:
        # We add the shards in the wallet
        Wallet     = RedisWallet(Creature.id)
        walletammo = getattr(Wallet, itemmeta['caliber'])
        neededammo = itemmeta['max_ammo'] - Item.ammo

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
        Item.ammo = neededammo
        # We remove the ammo from wallet
        setattr(Wallet, itemmeta['caliber'], walletammo - neededammo)
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
        msg = f'{h} Reload Query KO (weaponid:{Item.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Reload Query OK (weaponid:{Item.id})'
        logger.debug(msg)
        Pa = RedisPa(creatureuuid=creatureuuid)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": Pa.as_dict()['red'],
                    "blue": Pa.as_dict()['blue'],
                    "weapon": Item.as_dict(),
                },
            }
        ), 200
