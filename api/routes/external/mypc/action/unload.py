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
# API: POST /mypc/<uuid:creatureuuid>/action/unload/<uuid:weaponuuid>
@jwt_required()
def unload(creatureuuid, weaponuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    # Retrieving weapon stats
    try:
        Item = RedisItem(itemuuid=weaponuuid)
    except Exception as e:
        msg = f'{h} Item Query KO (weaponid:{weaponuuid}) [{e}]'
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
        if Item.ammo == 0:
            msg = f'{h} Item is already empty (weaponid:{Item.id})'
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    Pa = RedisPa(creatureuuid=creatureuuid)
    if Pa.bluepa < 2:
        # Not enough PA to unload
        msg = f'{h} Not enough PA to unload (weaponid:{Item.id})'
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

    try:
        # We add the shards in the wallet
        Wallet = RedisWallet(Creature.id)
        # We add the ammo to wallet
        walletammo = getattr(Wallet, itemmeta['caliber'])
        setattr(Wallet, itemmeta['caliber'], walletammo + Item.ammo)
        # We unload the weapon
        Item.ammo = 0
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
        msg = f'{h} Unload Query KO (weaponid:{Item.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Unload Query OK (weaponid:{Item.id})'
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
