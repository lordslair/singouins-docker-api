# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger

from nosql.metas import metaNames
from nosql.models.RedisAuction import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem import RedisItem

from subcommands.auction._autocomplete import get_singouin_auctioned_item_list
from subcommands.singouin._autocomplete import get_singouins_list

from variables import rarity_item_types_discord


def remove(group_auction):
    @group_auction.command(
        description='[@Singouins role] Remove an item from the Auction House',
        default_permission=False,
        name='remove',
        )
    @option(
        "selleruuid",
        description="Seller UUID",
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
        autocomplete=get_singouin_auctioned_item_list
        )
    async def remove(
        ctx: discord.ApplicationContext,
        selleruuid: str,
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
            f'/{group_auction} remove {selleruuid} {itemuuid}'
            )

        Creature = RedisCreature(creatureuuid=selleruuid)
        Item = RedisItem(itemuuid=itemuuid)

        if Item.id is None:
            msg = 'Item NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    )
                )
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return
        if Item.bearer != Creature.id:
            msg = 'Item does not belong to you'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    )
                )
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO ({msg})')
            return

        try:
            RedisAuction(auctionuuid=Item.id).destroy()
        except Exception as e:
            description = f'Auction-Remove Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
        else:
            embed = discord.Embed(
                title="Removed from the Auction House:",
                description=(
                    f"{rarity_item_types_discord[Item.rarity]} "
                    f"**{metaNames[Item.metatype][Item.metaid]['name']}**"
                    ),
                colour=discord.Colour.green()
            )

        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Auction Query OK')
        return
