# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from mysql.methods.fn_creature  import fn_creature_get
from mysql.methods.fn_inventory import fn_item_get_one, fn_item_owner_set

from nosql.models.RedisAuction  import RedisAuction
from nosql.models.RedisWallet   import RedisWallet

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/auction/{itemid}
def creature_auction_sell(creatureid, itemid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    duration = request.json.get('duration')
    price    = request.json.get('price')

    if not isinstance(duration, int):
        msg = f'Duration should be an INT (duration:{duration})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(price, int):
        msg = f'Price should be an INT (price:{price})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
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

    item    = fn_item_get_one(itemid)
    if item is None:
        msg = f'{h} Item not found (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if item.bearer != creature.id:
        msg = f'{h} Item does not belong to you (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if item.bound_type is False:
        msg = f'{h} Item should not be bound (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We add the Item into the Auctions
    try:
        sell = RedisAuction().sell(creature, item, price, duration)
    except Exception as e:
        msg = f'{h} Auction Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if sell is False:
            msg = f'{h} Auction Query KO - Already Exists'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 409
        elif sell:
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "creature": creature,
                        "auction": {
                            "duration_base": sell.duration_base,
                            "duration_left": sell.duration_base,
                            "id": sell.id,
                            "meta_id": sell.meta.id,
                            "meta_name": sell.meta.name,
                            "price": sell.price,
                            "rarity": sell.item.rarity,
                            "seller_id": sell.seller.id,
                            "seller_name": sell.seller.name,
                            },
                        },
                }
            ), 201
        else:
            msg = f'{h} Auction Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: DELETE /internal/creature/{creatureid}/auction/{itemid}
def creature_auction_remove(creatureid, itemid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
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

    item    = fn_item_get_one(itemid)
    if item is None:
        msg = f'{h} Item not found (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if item.bearer != creature.id:
        msg = f'{h} Item does not belong to you (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We remove the Item into the Auctions
    try:
        remove = RedisAuction().destroy(item)
    except Exception as e:
        msg = f'{h} Auction Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if remove is True:
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'{h} Auction Query KO '
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /internal/creature/{creatureid}/auction/{itemid}
def creature_auction_buy(creatureid, itemid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
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

    item    = fn_item_get_one(itemid)
    if item is None:
        msg = f'{h} Item not found (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We remove the Item into the Auctions
    try:
        auction = RedisAuction().get(item)
    except Exception as e:
        msg = f'{h} Auction Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if auction is False:
            msg = f'Auction not found (itemid:{itemid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 404

        seller = fn_creature_get(None, auction.seller_id)[3]
        if seller is None:
            msg = f'Creature not found (seller_id:{auction.seller_id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        if auction:
            # We delete the auction
            RedisAuction().destroy(item)
            # We do the financial transaction
            buyer_wallet = RedisWallet(creature)
            buyer_wallet.incr(
                'bananas',
                count=(auction.price * (-1))
                )
            seller_wallet = RedisWallet(seller)
            seller_wallet.incr(
                'bananas',
                count=round(auction.price * 0.9)
                )
            # We change the Item owner
            item = fn_item_owner_set(item.id, creature.id)
            if item is None:
                msg = f'{h} Auction Query KO'
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            # We are done
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "creature": creature,
                        "item": item,
                        "auction": {
                            "duration_base": auction.duration_base,
                            "duration_left": 0,
                            "id": auction.id,
                            "meta_id": auction.meta_id,
                            "meta_name": auction.meta_name,
                            "price": auction.price,
                            "rarity": auction.rarity,
                            "seller_id": auction.seller_id,
                            "seller_name": auction.seller_name,
                            }
                    },
                }
            ), 200
        else:
            msg = f'{h} Auction Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: GET /internal/creature/{creatureid}/auction/{itemid}
def creature_auction_get(creatureid, itemid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
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

    item    = fn_item_get_one(itemid)
    if item is None:
        msg = f'{h} Item not found (itemid:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We get the Item from the Auctions
    try:
        auction = RedisAuction().get(item)
    except Exception as e:
        msg = f'{h} Auction Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if auction:
            # We are done
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "creature": creature,
                        "item": item,
                        "auction": {
                            "duration_base": auction.duration_base,
                            "duration_left": 0,
                            "id": auction.id,
                            "meta_id": auction.meta_id,
                            "meta_name": auction.meta_name,
                            "price": auction.price,
                            "rarity": auction.rarity,
                            "seller_id": auction.seller_id,
                            "seller_name": auction.seller_name,
                            }
                    },
                }
            ), 200
        else:
            msg = f'{h} Auction Query KO'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /internal/creature/{creatureid}/auctions
def creature_auctions_search(creatureid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = 'Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    metaid   = request.json.get('metaid', None)
    metatype = request.json.get('metatype', None)

    if metatype is None:
        msg = f'Meta Type is mandatory (metatype:{metatype})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if metaid and not isinstance(metaid, int):
        msg = f'Meta ID should be an INT (metaid:{metaid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if metatype and not isinstance(metatype, str):
        msg = f'Meta Type should be a STR (metatype:{metatype})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Pre-flight checks
    creature    = fn_creature_get(None, creatureid)[3]
    if creature is None:
        msg = f'Creature not found (creatureid:{creatureid})'
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

    # We get the Item from the Auctions
    try:
        auctions = RedisAuction().search(metaid=metaid, metatype=metatype)
    except Exception as e:
        msg = f'{h} Auctions Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # We are done
        msg = f'{h} Auctions Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "creature": creature,
                    "auctions": auctions,
                },
            }
        ), 200
