# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from subcommands.auction._autocomplete import get_auctioned_item_list
from subcommands.auction._view import buyView
from subcommands.singouin._autocomplete import get_singouins_list


def buy(group_auction):
    @group_auction.command(
        description='[@Singouins role] Buy an item in the Auction House',
        default_permission=False,
        name='buy',
        )
    @option(
        "buyeruuid",
        description="Singouin UUID",
        autocomplete=get_singouins_list
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
        "itemuuid",
        description="Item UUID",
        autocomplete=get_auctioned_item_list
        )
    async def buy(
        ctx: discord.ApplicationContext,
        buyeruuid: str,
        metatype: str,
        itemuuid: str,
    ):

        name = ctx.author.name
        # Pre-flight checks
        if ctx.channel.type is discord.ChannelType.private:
            channel = ctx.channel.type
        else:
            channel = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/auction buy {buyeruuid} {itemuuid}'
            )

        try:
            embed = discord.Embed(
                title='Aknowledgement required',
                description=(
                    'Are you sure you really want to buy this item ?\n'
                    '-> Currency will be removed from your Wallet\n'
                    '-> Item will be added to your Inventory'
                    ),
                colour=discord.Colour.blue()
            )
            await ctx.respond(
                embed=embed,
                view=buyView(ctx, buyeruuid, itemuuid),
                )
        except Exception as e:
            description = f'Auction-Buy View KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
        else:
            logger.info(f'[#{channel}][{name}] └──> Auction View OK')
            return
