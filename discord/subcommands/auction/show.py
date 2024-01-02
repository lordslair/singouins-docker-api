# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from nosql.models.RedisSearch import RedisSearch

from subcommands.auction._tools import human_time
from subcommands.singouin._autocomplete import get_mysingouins_list

from variables import rarity_item_types_discord


def show(group_auction, bot):
    @group_auction.command(
        description='[@Singouins role] Show your items in the Auction House',
        default_permission=False,
        name='show',
        )
    @option(
        "selleruuid",
        description="Seller UUID",
        autocomplete=get_mysingouins_list
        )
    async def show(
        ctx: discord.ApplicationContext,
        selleruuid: str,
    ):

        name = ctx.author.name
        # Pre-flight checks
        if ctx.channel.type is discord.ChannelType.private:
            channel = ctx.channel.type
        else:
            channel = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_auction} show {selleruuid}'
            )

        Auctions = RedisSearch().auction(
            query=(f'@sellerid:{selleruuid.replace("-", " ")}')
            )

        if len(Auctions.results) == 0:
            msg = 'You are not selling anything in the Auction House'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.debug(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return

        # Dirty Gruik to find the max(len(metaname))
        metaname_width = max(
            len(Auction.metaname) for Auction in Auctions.results
            )
        # We need to put a floor to respect the Tableau header
        metaname_width = max(9, metaname_width)

        # We add a header for the results "Tableau"
        itemname, price, end = 'Item name', 'Price', 'End'
        description = (
                f"💱 `{itemname:{metaname_width}}` | "
                f"`{price:8}` | "
                f"`{end:7}`"
                f"\n"
                )
        itemname = '-' * (metaname_width + 3)
        description += (
                f"`{itemname:{metaname_width}}` | "
                f"`--------` | "
                f"`-------`"
                f"\n"
                )
        # We loop on items retrieved in Auctions
        for Auction in Auctions.results:
            description += (
                f"{rarity_item_types_discord[Auction.rarity]} "
                f"`{Auction.metaname:{metaname_width}}` | "
                f"`{Auction.price:5}` "
                f"{discord.utils.get(bot.emojis, name='moneyB')} | "
                f"`{human_time(Auction.duration_left):7}`"
                "\n"
                )

        await ctx.respond(
            embed=discord.Embed(
                title=f'Your auctions ({len(Auctions.results)}):',
                description=description,
                colour=discord.Colour.green()
                ),
            ephemeral=True,
            )
        logger.info(f'[#{channel}][{name}] └──> Auction Query OK')
        return
