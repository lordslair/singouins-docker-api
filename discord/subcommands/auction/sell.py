# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from nosql.models.RedisAuction import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem import RedisItem

from subcommands.auction._autocomplete import (
    get_singouin_auctionable_item_list,
    )
from subcommands.singouin._autocomplete import get_mysingouins_list

from variables import rarity_item_types_discord


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

        name = ctx.author.name
        # Pre-flight checks
        if ctx.channel.type is discord.ChannelType.private:
            channel = ctx.channel.type
        else:
            channel = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_auction} sell {selleruuid} {itemuuid} {price}'
            )

        Creature = RedisCreature(creatureuuid=selleruuid)
        Item = RedisItem(itemuuid=itemuuid)

        if Item.id is None:
            msg = 'Item NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return
        if Item.bearer != Creature.id:
            msg = 'Item does not belong to you'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return
        if Item.bound_type is False:
            msg = 'Item should not be bound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return
        if hasattr(RedisAuction(auctionuuid=itemuuid), 'id'):
            msg = 'Item already sold in the Auction House'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return

        try:
            Auction = RedisAuction().new(Creature, Item, price, 172800)
        except Exception as e:
            description = f'Auction-Sell Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return

        embed = discord.Embed(
            title="Added from the Auction House:",
            description=(
                f"{rarity_item_types_discord[Item.rarity]} "
                f"**{Auction.metaname}** (Price:{price})"
                ),
            colour=discord.Colour.green(),
            )
        embed.set_footer(text=f"ItemUUID: {Item.id}")
        await ctx.respond(embed=embed, ephemeral=True)
        logger.info(f'[#{channel}][{name}] └──> Auction Query OK')
        return
