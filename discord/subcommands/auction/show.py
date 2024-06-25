# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from mongo.models.Auction import AuctionDocument

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.auction._tools import auction_time_left

from variables import item_types_discord, metaNames, rarity_item_types_discord


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

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_auction} show {selleruuid}')

        Auctions = AuctionDocument.objects(seller__id=selleruuid)

        if Auctions.count() == 0:
            msg = 'You are not selling anything in the Auction House'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.debug(f'{h} └──> Auction-Show Query KO ({msg})')
            return

        # Dirty Gruik to find the max(len(metaname))
        w = max(len(Auction.item.name) for Auction in Auctions)
        # We need to put a floor to respect the Tableau header
        w = max(9, w)

        # We add a header for the results "Tableau"
        itemname, price, end = 'Item name', 'Price', 'End'
        description = f"ℹ️ 💱 `{itemname:{w}}` | `{price:8}` | `{end:8}`\n"
        itemname = '-' * (w + 6)
        description += f"`{itemname:{w}}` | `--------` | `--------`\n"
        # We loop on items retrieved in Auctions
        for Auction in Auctions:
            itemname = metaNames[Auction.item.metatype][Auction.item.metaid]['name']
            description += (
                f"{item_types_discord[Auction.item.metatype]} "
                f"{rarity_item_types_discord[Auction.item.rarity]} "
                f"`{itemname:{w}}` | "
                f"`{Auction.price:5}` "
                f"{discord.utils.get(bot.emojis, name='moneyB')} | "
                f"`{auction_time_left(Auction.created):8}`"
                "\n"
                )

        await ctx.respond(
            embed=discord.Embed(
                title=f'Your auctions ({Auctions.count()}):',
                description=description,
                colour=discord.Colour.green()
                ),
            ephemeral=True,
            )
        logger.info(f'{h} └──> Auction-Show Query OK')
        return
