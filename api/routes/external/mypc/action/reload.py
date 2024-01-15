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
# API: POST /mypc/<uuid:creatureuuid>/action/reload/<uuid:itemuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_item_exists
@check_user_exists
@check_creature_owned
def reload(creatureuuid, itemuuid):
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
    if g.Item.ammo == itemmeta['max_ammo']:
        msg = f'{g.h} Item is already loaded ItemUUID({g.Item.id})'
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    Pa = RedisPa(creatureuuid=g.Creature.id)
    if Pa.redpa < itemmeta['pas_reload']:
        # Not enough PA to reload
        msg = f'{g.h} Not enough PA to reload'
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
        Wallet     = RedisWallet(creatureuuid=g.Creature.id)
        walletammo = getattr(Wallet, itemmeta['caliber'])
        neededammo = itemmeta['max_ammo'] - g.Item.ammo

        if walletammo < neededammo:
            # Not enough ammo to reload
            msg = (f"{g.h} Not enough Ammo to reload "
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
        g.Item.ammo = neededammo
        # We remove the ammo from wallet
        setattr(Wallet, itemmeta['caliber'], walletammo - neededammo)
        # We consume the PA
        RedisPa(creatureuuid=g.Creature.id).consume(
            redpa=itemmeta['pas_reload']
            )
        # Wa add HighScore
        RedisHS(creatureuuid=g.Creature.id).incr('action_reload')
        # We create the Creature Event
        RedisEvent().new(
            action_src=g.Creature.id,
            action_dst=None,
            action_type='action/reload',
            action_text='Reloaded a weapon',
            action_ttl=30 * 86400
            )
    except Exception as e:
        msg = f'{g.h} Reload Query KO ItemUUID({g.Item.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Reload Query OK ItemUUID({g.Item.id})'
        logger.debug(msg)
        Pa = RedisPa(creatureuuid=g.Creature.id)
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
