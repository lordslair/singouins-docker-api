# -*- coding: utf8 -*-

import datetime
import discord

from discord.commands import option
from loguru import logger

from mongo.models.Auction import AuctionDocument
from mongo.models.Item import ItemDocument

from subcommands.auction._autocomplete import get_singouin_auctions_list
from subcommands.singouin._autocomplete import get_mysingouins_list

from variables import env_vars, item_types_discord, rarity_item_types_discord


def remove(group_auction):
    @group_auction.command(
        description='[@Singouins role] Remove an item from the Auction House',
        default_permission=False,
        name='remove',
        )
    @option(
        "selleruuid",
        description="Seller UUID",
        autocomplete=get_mysingouins_list
        )
    @option(
        "metatype",
        description="Item Type",
        autocomplete=discord.utils.basic_autocomplete(
            [
                discord.OptionChoice("Armor", value='armor'),
                discord.OptionChoice("Weapon", value='weapon'),
                ]
            )
        )
    @option(
        "auctionuuid",
        description="Auction UUID",
        autocomplete=get_singouin_auctions_list
        )
    async def remove(
        ctx: discord.ApplicationContext,
        selleruuid: str,
        metatype: str,
        auctionuuid: str,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_auction} remove {selleruuid} {auctionuuid}')

        try:
            Auction = AuctionDocument.objects(_id=auctionuuid, seller__id=selleruuid).get()  # noqa: E501
        except AuctionDocument.DoesNotExist:
            msg = 'Auction NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Auction-Remove Query KO ({msg})')
            return

        try:
            Item = ItemDocument.objects(_id=Auction.item.id, auctioned=True, bearer=selleruuid).get()  # noqa: E501
        except ItemDocument.DoesNotExist:
            msg = 'Item NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Auction-Remove Query KO ({msg})')
            return

        try:
            Auction.delete()
            Item.auctioned = False
            Item.updated = datetime.datetime.utcnow()
            Item.save()
        except Exception as e:
            description = f'Auction-Remove Query KO [{e}]'
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
            title="Removed from the Auction House:",
            description=(
                f"> {item_types_discord[Item.metatype]} "
                f"{rarity_item_types_discord[Item.rarity]} **{Auction.item.name}**"
                ),
            colour=discord.Colour.green(),
            )
        embed.set_footer(text=f"ItemUUID: {Item.id}")

        # We add Thumbnail
        URI_PNG = f'sprites/{Item.metatype}s/{Item.metaid}.png'
        logger.trace(f"[embed.thumbnail] {env_vars['URL_ASSETS']}/{URI_PNG}")
        embed.set_thumbnail(url=f"{env_vars['URL_ASSETS']}/{URI_PNG}")

        await ctx.respond(embed=embed, ephemeral=True)
        logger.info(f'{h} └──> Auction-Remove Query OK')
        return
