# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.metas                import metaNames
from nosql.models.RedisEvent    import RedisEvent
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisWallet   import RedisWallet

from utils.decorators import (
    check_creature_exists,
    check_item_exists,
    check_user_exists,
    check_creature_owned,
    )


#
# Routes /mypc/<uuid:creatureuuid>/action
#
# API: POST /mypc/<uuid:creatureuuid>/action/unload/<uuid:itemuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_user_exists
@check_item_exists
@check_creature_owned
def unload(creatureuuid, itemuuid):
    itemmeta = metaNames[g.Item.metatype][g.Item.metaid]
    if itemmeta['pas_reload'] is None:
        msg = f'{g.h} Item is not reloadable ItemUUID({g.Item.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if g.Item.ammo == 0:
        msg = f'{g.h} Item is already empty Item({g.Item.id})'
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
        msg = f'{g.h} Not enough PA to unload Item({g.Item.id})'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": {
                    "red": RedisPa(g.Creature)._asdict()['red'],
                    "blue": RedisPa(g.Creature)._asdict()['blue'],
                    "weapon": None,
                },
            }
        ), 200

    try:
        # We add the shards in the wallet
        Wallet = RedisWallet(g.Creature.id)
        # We add the ammo to wallet
        walletammo = getattr(Wallet, itemmeta['caliber'])
        setattr(Wallet, itemmeta['caliber'], walletammo + g.Item.ammo)
        # We unload the weapon
        g.Item.ammo = 0
        # We consume the PA
        RedisPa(creatureuuid=creatureuuid).consume(bluepa=2)
        # We add HighScore
        RedisHS(creatureuuid=creatureuuid).incr('action_unload')
        # We create the Creature Event
        RedisEvent().new(
            action_src=g.Creature.id,
            action_dst=None,
            action_type='action/unload',
            action_text='Unloaded a weapon',
            action_ttl=30 * 86400
            )
    except Exception as e:
        msg = f'{g.h} Unload Query KO Item({g.Item.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Unload Query OK Item({g.Item.id})'
        logger.debug(msg)
        Pa = RedisPa(creatureuuid=creatureuuid)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "red": Pa.as_dict()['red'],
                    "blue": Pa.as_dict()['blue'],
                    "weapon": g.Item.as_dict(),
                },
            }
        ), 200
