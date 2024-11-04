# -*- coding: utf8 -*-

import discord

from loguru import logger

from mongo.models.Auction import AuctionDocument
from mongo.models.Item import ItemDocument

from variables import metaIndexed, rarity_item_types_emoji


async def get_auctioned_item_list(ctx: discord.AutocompleteContext):
    try:
        Auctions = AuctionDocument.objects(item__metatype=ctx.options['metatype'])
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
    else:
        db_list = []
        for Auction in Auctions:
            eh = rarity_item_types_emoji[Auction.item.rarity]
            db_list.append(
                discord.OptionChoice(
                    f"{eh} {Auction.item.name} (Price:{Auction.price})",
                    value=f"{Auction.id}"
                    )
                )
        return db_list


async def get_singouin_auctionable_item_list(ctx: discord.AutocompleteContext):
    try:
        Items = ItemDocument.objects(
            auctioned=False,
            bearer=ctx.options['selleruuid'],
            bound_type='BoE',
            )
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
    else:
        db_list = []
        for Item in Items:
            eh = rarity_item_types_emoji[Item.rarity]
            name = metaIndexed[Item.metatype][Item.metaid]['name']
            db_list.append(discord.OptionChoice(f"{eh} {name}", value=f"{Item.id}"))
    return db_list


async def get_singouin_auctions_list(ctx: discord.AutocompleteContext):
    try:
        Auctions = AuctionDocument.objects(
            seller__id=ctx.options["selleruuid"],
            item__metatype=ctx.options['metatype'],
            )
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')

    db_list = []
    for Auction in Auctions:
        eh = rarity_item_types_emoji[Auction.item.rarity]
        db_list.append(
            discord.OptionChoice(
                f"{eh} {Auction.item.name} (Price:{Auction.price})",
                value=f"{Auction.id}"
                )
            )
    return db_list
