# -*- coding: utf8 -*-

import discord
import os

from loguru          import logger

from nosql.metas import (
    metaNames,
    )
from nosql.models.RedisAuction  import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem

from utils.variables    import (
    rarity_item_types_discord,
    )

#
# ENV Variables
#

PCS_URL = os.environ.get("SEP_PCS_URL")

#
# Embeds
#


def embed_auction_search(metatype, metaid):
    try:
        if metaid and isinstance(metaid, str):
            metaid = int(metaid)
            metaname = metaNames[metatype][metaid]
            search = f'*{metaname}*'
        else:
            metaid = None
            metaname = None
            search = '*'
    except Exception as e:
        msg = f'Meta ID parsing failed [{e}]'
        logger.error(msg)

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
        msg = f'Auction search KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        if len(Auctions) == 0:
            msg = 'Auction House empty'
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.orange()
            )
            return embed

        # We loop on items retrieved in Auctions
        description = ''
        for item in Auctions:
            description += (
                f"{rarity_item_types_discord[item['rarity']]} "
                f"{item['metaname']} | "
                f"**Price**: {item['price']} | "
                f"**Seller**: {item['sellername']}"
                "\n"
                )

        embed = discord.Embed(
            title=f'Searched for {metatype.upper()}:{search}',
            description=description,
            colour=discord.Colour.green()
        )
        return embed


def embed_auction_remove(creatureuuid, itemuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    Item = RedisItem(Creature).get(itemuuid)

    if Item is None:
        msg = 'Item NotFound'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed
    if Item.bearer != Creature.id:
        msg = 'Item does not belong to you'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed

    try:
        RedisAuction().destroy(Item.id)
    except Exception as e:
        msg = f'Auction remove KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        embed = discord.Embed(
            title="Removed from the Auction House:",
            description=(
                f"{rarity_item_types_discord[Item.rarity]} "
                f"**{metaNames[Item.metatype][Item.metaid]['name']}**"
                ),
            colour=discord.Colour.green()
        )
        return embed


def embed_auction_sell(creatureuuid, itemuuid, price):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    Item = RedisItem(Creature).get(itemuuid)

    if Item is None:
        msg = 'Item NotFound'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed
    if Item.bearer != Creature.id:
        msg = 'Item does not belong to you'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed
    if Item.bound_type is False:
        msg = 'Item should not be bound'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed

    if RedisAuction().get(Item.id):
        msg = 'Item already sold in the Auction House'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed

    try:
        Auction = RedisAuction().new(Creature, Item, price, 172800)
    except Exception as e:
        msg = f'Auction sell KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        embed = discord.Embed(
            title='Added to the Auction House:',
            description=(
                f"{rarity_item_types_discord[Item.rarity]} "
                f"**{Auction.metaname}** (Price:{price})"
                ),
            colour=discord.Colour.green()
        )
        return embed
