# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Auction import AuctionDocument  # noqa: E402
from mongo.models.Creature import CreatureDocument  # noqa: E402
from mongo.models.Item import ItemDocument  # noqa: E402
from nosql.metas import metaNames  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))

ITEM_META_TYPE = 'weapon'
ITEM_META_ID = 37
ITEM_META = metaNames[ITEM_META_TYPE][ITEM_META_ID]

AUCTION_PRICE = 100


def test_mongodb_auction_new():
    """
    Creating a new AuctionDocument
    """

    Creature = CreatureDocument.objects(_id=CREATURE_ID).get()
    assert Creature
    Item = ItemDocument.objects(bearer=CREATURE_ID, metaid=ITEM_META_ID).get()
    assert Item

    newAuction = AuctionDocument(
        item=Item,
        price=AUCTION_PRICE,
        seller=Creature,
    )
    newAuction.save()

    assert newAuction.seller.id == Creature.id
    assert newAuction.price == AUCTION_PRICE
    assert newAuction.item.id == Item.id


def test_mongodb_auction_get_ok():
    """
    Querying a AuctionDocument
    """
    pass


def test_mongodb_auction_search_ok():
    """
    Searching a Item
    """
    Auction = AuctionDocument.objects(seller=CREATURE_ID)
    assert Auction.count() == 1
    assert Auction.get()


def test_mongodb_auction_del_ok():
    """
    Removing a AuctionDocument
    """

    Auctions = AuctionDocument.objects(seller=CREATURE_ID)
    if Auctions.count() > 0:
        for Auction in Auctions:
            Auctions.delete()

    assert Auctions.count() == 0


def test_mongodb_auction_del_ko():
    """
    Removing a AuctionDocument
    > Expected to fail
    """

    assert AuctionDocument.objects(seller=CREATURE_ID).delete() == 0


def test_mongodb_auction_search_empty():
    """
    Searching a AuctionDocument
    > Expected to fail
    """

    assert AuctionDocument.objects(seller=CREATURE_ID).count() == 0
