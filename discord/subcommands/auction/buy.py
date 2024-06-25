# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from subcommands.auction._autocomplete import get_auctioned_item_list
from subcommands.auction._view import buyView
from subcommands.singouin._autocomplete import get_mysingouins_list


def buy(group_auction):
    @group_auction.command(
        description='[@Singouins role] Buy an item in the Auction House',
        default_permission=False,
        name='buy',
        )
    @option(
        "buyeruuid",
        description="Singouin UUID",
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
        autocomplete=get_auctioned_item_list
        )
    async def buy(
        ctx: discord.ApplicationContext,
        buyeruuid: str,
        metatype: str,
        auctionuuid: str,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_auction} buy {buyeruuid} {auctionuuid}')

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
                view=buyView(ctx, buyeruuid, auctionuuid),
                ephemeral=True,
                )
        except Exception as e:
            description = f'Auction-Buy View KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return
        else:
            logger.info(f'{h} └──> Auction-Buy View OK')
            return
