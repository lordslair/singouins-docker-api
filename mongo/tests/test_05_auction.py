# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('mongo'))
sys.path.append(LOCAL_PATH)

from mongo.models.Auction import AuctionDocument, AuctionItem, AuctionSeller  # noqa: E402
from mongo.models.Creature import CreatureDocument  # noqa: E402
from mongo.models.Item import ItemDocument  # noqa: E402
from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon  # noqa: E402

metaNames = {
    'armor': [doc.to_mongo().to_dict() for doc in MetaArmor.objects()],
    'weapon': [doc.to_mongo().to_dict() for doc in MetaWeapon.objects()],
    'race': [doc.to_mongo().to_dict() for doc in MetaRace.objects()]
}

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
    Item = ItemDocument.objects(
        bearer=CREATURE_ID,
        metatype=ITEM_META_TYPE,
        metaid=ITEM_META_ID).get()
    assert Item

    newAuction = AuctionDocument(
        item=AuctionItem(
            id=Item.id,
            metaid=Item.metaid,
            metatype=Item.metatype,
            name=metaNames[Item.metatype][Item.metaid]['name'],
            rarity=Item.rarity,
        ),
        price=AUCTION_PRICE,
        seller=AuctionSeller(
            id=Creature.id,
            name=Creature.name,
        ),
    )
    newAuction.save()

    assert newAuction.seller.id == Creature.id
    assert newAuction.price == AUCTION_PRICE
    assert newAuction.item.id == Item.id


def test_mongodb_auction_get():
    """
    Querying a AuctionDocument
    """
    pass


def test_mongodb_auction_search():
    """
    Searching a Item
    """
    Auction = AuctionDocument.objects(seller__id=CREATURE_ID)
    assert Auction.count() == 1
    assert Auction.get()


def test_mongodb_auction_del():
    """
    Removing a AuctionDocument
    """

    Auctions = AuctionDocument.objects(seller__id=CREATURE_ID)
    if Auctions.count() > 0:
        for Auction in Auctions:
            Auctions.delete()

    assert Auctions.count() == 0
