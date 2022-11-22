# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger

from nosql.models.RedisAuction  import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisWallet   import RedisWallet

from variables                  import API_INTERNAL_TOKEN

#
# Routes /internal
#


# /internal/creature/*
# API: PUT /internal/creature/{creatureid}/auction/{itemid}
def creature_auction_sell(creatureid, itemid):
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = f'{h} Missing JSON in request'
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
        msg = f'{h} Duration should be an INT (duration:{duration})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(price, int):
        msg = f'{h} Price should be an INT (price:{price})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    Item = RedisItem(Creature).get(itemid)
    if Item is None:
        msg = f'{h} Item Query KO - NotFound (Item.id:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Item.bearer != Creature.id:
        msg = f'{h} Item does not belong to you (Item.id:{Item.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Item.bound_type is False:
        msg = f'{h} Item should not be bound (Item.id:{Item.id})'
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
        Auction = RedisAuction().new(Creature, Item, price, duration)
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
        if Auction is False:
            msg = f'{h} Auction Query KO - Already Exists'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 409
        elif Auction:
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "creature": Creature._asdict(),
                        "auction": Auction._asdict(),
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
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Item = RedisItem(Creature).get(itemid)
    if Item is None:
        msg = f'{h} Item Query KO - NotFound (Item.id:{itemid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Item.bearer != Creature.id:
        msg = f'{h} Item does not belong to you (Item.id:{Item.id})'
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
        AuctionDeleted = RedisAuction().destroy(Item.id)
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
        if AuctionDeleted:
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Item._asdict(),
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
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Item = RedisItem(Creature).get(itemid)
    if Item is None:
        msg = f'{h} Item Query KO - NotFound (Item.id:{itemid})'
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
        Auction = RedisAuction().get(Item.id)
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
        if Auction is False:
            msg = f'{h} Auction Query KO - NotFound (Item.id:{itemid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 404

        CreatureSeller = RedisCreature().get(Auction.sellerid)
        if CreatureSeller is None:
            msg = f'Creature not found (sellerid:{Auction.sellerid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        if Auction:
            # We delete the auction
            RedisAuction().destroy(Item.id)
            # We do the financial transaction
            buyer_wallet = RedisWallet(Creature)
            buyer_wallet.incr(
                'bananas',
                count=(Auction.price * (-1))
                )
            seller_wallet = RedisWallet(CreatureSeller)
            seller_wallet.incr(
                'bananas',
                count=round(Auction.price * 0.9)
                )
            # We change the Item owner
            try:
                Item.bearer = Creature.id
            except Exception as e:
                msg = f'{h} Auction Query KO [{e}]'
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
                        "creature": Creature._asdict(),
                        "item": Item._asdict(),
                        "auction": Auction._asdict(),
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
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403

    Item = RedisItem(Creature).get(itemid)
    if Item is None:
        msg = f'{h} Item Query KO - NotFound (Item.id:{itemid})'
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
        Auction = RedisAuction().get(Item.id)
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
        if Auction:
            # We are done
            msg = f'{h} Auction Query OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "creature": Creature._asdict(),
                        "item": Item._asdict(),
                        "auction": Auction._asdict(),
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
    Creature = RedisCreature().get(creatureid)
    # Pre-flight checks
    if Creature is None:
        msg = '[Creature.id:None] Creature NotFound'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        h = f'[Creature.id:{Creature.id}]'  # Header for logging

    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'{h} Token not authorized'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 403
    if not request.is_json:
        msg = f'{h} Missing JSON in request'
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

    # We get the Item from the Auctions
    try:
        if metatype and metaid:
            query = f'(@metatype:{metatype}) & (@metaid:[{metaid} {metaid}])'
        elif metatype:
            query = f'@metatype:{metatype}'
        elif metaid:
            query = f'@metaid:[{metaid} {metaid}]'
        Auctions = RedisAuction().search(query=query)
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
                    "creature": Creature._asdict(),
                    "auctions": Auctions,
                },
            }
        ), 200
