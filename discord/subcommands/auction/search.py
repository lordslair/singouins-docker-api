# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from nosql.metas import metaNames
from nosql.models.RedisSearch import RedisSearch

from subcommands.godmode._autocomplete import get_metanames_list

from variables import rarity_item_types_discord


def search(group_auction, bot):
    @group_auction.command(
        description='[@Singouins role] Search in the Auction House',
        default_permission=False,
        name='search',
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
        "metaid",
        description="Item Name",
        autocomplete=get_metanames_list,
        required=False,
        )
    async def search(
        ctx: discord.ApplicationContext,
        metatype: str,
        metaid: str,
    ):

        name = ctx.author.name
        # Pre-flight checks
        if ctx.channel.type is discord.ChannelType.private:
            channel = ctx.channel.type
        else:
            channel = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_auction} search {metatype} {metaid}'
            )

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
                query = (
                    f'(@metatype:{metatype}) & '
                    f'(@metaid:[{metaid} {metaid}])'
                    )
            elif metatype:
                query = f'@metatype:{metatype}'
            elif metaid:
                query = f'@metaid:[{metaid} {metaid}]'
            Auctions = RedisSearch().auction(query=query)
        except Exception as e:
            description = f'Auction-Search Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return

        if len(Auctions.results) == 0:
            description = 'No items were found matching these criterias.'
            logger.debug(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.orange(),
                    )
                )
            return

        # Dirty Gruik to find the max(len(metaname))
        metaname_width = max(
            len(Auction.metaname) for Auction in Auctions.results
            )
        # Dirty Gruik to find the max(len(sellername))
        sellername_width = max(
            len(Auction.sellername) for Auction in Auctions.results
            )

        # We add a header for the results "Tableau"
        itemname, price, seller, end = 'Item name', 'Price', 'Seller', 'End'
        description = (
                f"💱 `{itemname:{metaname_width}}` | "
                f"`{price:8}` | "
                f"`{end:4}` | "
                f"`{seller:{sellername_width}}`"
                f"\n"
                )
        itemname, seller = '-' * (metaname_width + 3), '-' * sellername_width
        description += (
                f"`{itemname:{metaname_width}}` | "
                f"`--------` | "
                f"`----` | "
                f"`{seller:{sellername_width}}`"
                f"\n"
                )
        # We loop on items retrieved in Auctions
        for Auction in Auctions.results:
            description += (
                f"{rarity_item_types_discord[Auction.rarity]} "
                f"`{Auction.metaname:{metaname_width}}` | "
                f"`{Auction.price:5}` "
                f"{discord.utils.get(bot.emojis, name='moneyB')} | "
                f"`~{Auction.duration_left // 3600:2}h` | "
                f"`{Auction.sellername:{sellername_width}}`"
                "\n"
                )

        embed = discord.Embed(
            title=f'Searched for {metatype.upper()}:{search}',
            description=description,
            colour=discord.Colour.green()
        )

        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Auction Search Query OK')
        return
