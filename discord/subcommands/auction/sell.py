# -*- coding: utf8 -*-

import datetime
import discord

from discord.commands import option
from loguru import logger

from mongo.models.Auction import AuctionDocument, AuctionItem, AuctionSeller
from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument

from subcommands.auction._autocomplete import get_singouin_auctionable_item_list
from subcommands.singouin._autocomplete import get_mysingouins_list

from variables import (
    env_vars,
    item_types_discord as itd,
    metaIndexed,
    rarity_item_types_discord as ritd,
    )


def sell(group_auction):
    @group_auction.command(
        description='[@Singouins role] Sell an item in the Auction House',
        default_permission=False,
        name='sell',
        )
    @option(
        "selleruuid",
        description="Seller UUID",
        autocomplete=get_mysingouins_list
        )
    @option(
        "itemuuid",
        description="Item UUID",
        autocomplete=get_singouin_auctionable_item_list
        )
    @option(
        "price",
        description="Price"
        )
    async def sell(
        ctx: discord.ApplicationContext,
        selleruuid: str,
        itemuuid: str,
        price: int,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_auction} sell {selleruuid} {itemuuid} {price}')

        try:
            Creature = CreatureDocument.objects(_id=selleruuid).get()
        except CreatureDocument.DoesNotExist:
            msg = 'Seller NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Auction-Sell Query KO ({msg})')
            return

        try:
            Item = ItemDocument.objects(
                _id=itemuuid,
                auctioned=False,
                bearer=selleruuid,
                bound_type='BoE',
                ).get()
        except ItemDocument.DoesNotExist:
            msg = 'Item NotFound or not matching criterias'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Auction-Sell Query KO ({msg})')
            return

        try:
            newAuction = AuctionDocument(
                item=AuctionItem(
                    id=Item.id,
                    metaid=Item.metaid,
                    metatype=Item.metatype,
                    name=metaIndexed[Item.metatype][Item.metaid]['name'],
                    rarity=Item.rarity,
                ),
                price=price,
                seller=AuctionSeller(
                    id=Creature.id,
                    name=Creature.name,
                ),
            )
            newAuction.save()

            Item.auctioned = True
            Item.updated = datetime.datetime.utcnow()
            Item.save()
        except Exception as e:
            description = f'Auction-Sell Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return

        embed = discord.Embed(
            title="Added to the Auction House:",
            description=f"> {itd[Item.metatype]} {ritd[Item.rarity]} **{newAuction.item.name}** (Price:{price})",  # noqa: E501
            colour=discord.Colour.green(),
            )
        embed.set_footer(text=f"ItemUUID: {Item.id}")

        # We add Thumbnail
        URI_PNG = f'sprites/{Item.metatype}s/{Item.metaid}.png'
        logger.trace(f"[embed.thumbnail] {env_vars['URL_ASSETS']}/{URI_PNG}")
        embed.set_thumbnail(url=f"{env_vars['URL_ASSETS']}/{URI_PNG}")

        await ctx.respond(embed=embed, ephemeral=True)
        logger.info(f'{h} └──> Auction-Sell Query OK')
        return
