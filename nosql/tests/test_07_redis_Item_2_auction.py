# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisCreature import RedisCreature  # noqa: E402
from nosql.models.RedisItem import RedisItem  # noqa: E402
from nosql.models.RedisAuction import RedisAuction  # noqa: E402
from nosql.models.RedisSearch import RedisSearch  # noqa: E402

CREATURE_NAME = "PyTest Creature"
CREATURE_ID   = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))
ACCOUNT_ID    = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'foobar'))

"""
Creating a new RedisItem
"""
Item = RedisItem().new(
    creatureuuid=CREATURE_ID,
    item_caracs={
        "metatype": 'weapon',
        "metaid": 32,
        "bound": True,
        "bound_type": 'BoP',
        "modded": False,
        "mods": None,
        "state": 100,
        "rarity": 'Common'
        }
    )


def test_redis_auction_new():
    """
    Creating a new RedisAuction
    """
    Creature = RedisCreature().new(
        name=CREATURE_NAME,
        raceid=4,
        gender=True,
        accountuuid=ACCOUNT_ID,
        instanceuuid=None,
    )

    Auction = RedisAuction().new(
        Creature=Creature,
        Item=Item,
        price=100,
        )

    assert Auction.id == Item.id
    assert Auction.seller.id == CREATURE_ID


def test_redis_auction_get_ok():
    """
    Querying a RedisAuction
    """
    Auction = RedisAuction(auctionuuid=Item.id)

    assert Auction.id == Item.id
    assert Auction.sellerid == CREATURE_ID


def test_redis_auction_search_ok():
    """
    Searching a Auction
    """
    id = Item.id.replace('-', ' ')
    Auctions = RedisSearch().auction(query=f'@id:{id}')

    Auction = Auctions.results_as_dict[0]
    assert Auction['sellerid'] == CREATURE_ID

    Auction = Auctions.results[0]
    assert Auction.sellerid == CREATURE_ID


def test_redis_auction_del():
    """
    Removing a RedisAuction
    """
    ret = RedisAuction(auctionuuid=Item.id).destroy()

    assert ret is True


def test_redis_auction_get_ko():
    """
    Querying a RedisAuction
    > Expected to fail
    """
    Auction = RedisAuction(auctionuuid=Item.id)

    assert Auction.hkey == 'auctions'
    assert hasattr(Auction, 'id') is False

    Auction = RedisAuction()

    assert Auction.hkey == 'auctions'
    assert hasattr(Auction, 'id') is False


def test_redis_auction_search_empty():
    """
    Searching a Auction
    > Expected to fail
    """
    id = Item.id.replace('-', ' ')
    Auctions = RedisSearch().auction(query=f'@id:{id}')

    assert len(Auctions.results) == 0


def test_redis_auction_cleanup():
    """
    Removing a RedisCreature
    """
    RedisCreature(creatureuuid=CREATURE_ID).destroy()
